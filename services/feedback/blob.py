from datetime import datetime
from fastapi import APIRouter, HTTPException
import os
import mysql.connector
from mysql.connector import connect, Error
from dotenv import load_dotenv

from send_alerts.verify_bd import insert_file_process
from services.connection import conectar, desconectar
from services.utils import image_to_byte_array

router = APIRouter()


IMAGES_PATH = 'classificador/classificadorIA/classificados/Não Autorizado'
QUEUE_PATH = 'classificador/classificadorIA/queue'

def get_images_from_directory(path):
    print("Get images")
    images = []
    for filename in os.listdir(path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            images.append((filename, os.path.join(path, filename)))
    return images

def save_image_blob(image_path):
    try:
        with open(image_path, 'rb') as file:
            blob = file.read()

        cnx, cur = conectar()
        query = "UPDATE tbl_imagens SET blob_imagens = %s WHERE path = %s"
        cur.execute(query, (blob, image_path))
        cnx.commit()
        print("Blob updated for: ", image_path)
    except Exception as e:
        print(f"Error saving blob: {str(e)}")
    finally:
        desconectar(cnx, cur)

def update_image_path(filename, new_path):
    try:
        query = "UPDATE tbl_imagens SET path = %s WHERE path LIKE %s"
        cnx, cur = conectar()
        cur.execute(query, (new_path, f"%{filename}%"))
        cnx.commit()
    except Exception as e:
        print(f"Error updating image path: {str(e)}")
    finally:
        desconectar(cnx, cur)

@router.get("/process-unauthorized-images")
async def process_unauthorized_images():
    images = get_images_from_directory(IMAGES_PATH)
    for filename, image_path in images:
        cnx, cur = conectar()
        try:
            existing_query = "SELECT COUNT(*) FROM tbl_imagens WHERE path = %s"
            cur.execute(existing_query, (image_path,))
            result = cur.fetchone()
            if result[0] > 0:
                update_image_path(filename, image_path)
                save_image_blob(image_path)
                print(f"Processed image: {filename}")
            else:
                print(f"Image does not exist in DB: {filename}")
        finally:
            desconectar(cnx, cur)
    return {"message": "Images processed successfully", "processed_count": len(images)}

@router.get("/process-queue-images")
async def process_queue_images():
    queue = get_images_from_directory(QUEUE_PATH)
    for filename, image_path in queue:
        cnx, cur = conectar()
        try:
            existing_query = "SELECT id_imagem FROM tbl_imagens WHERE path = %s"
            cur.execute(existing_query, (image_path,))
            result = cur.fetchone()

            if result:
                update_image_path(filename, image_path)
                save_image_blob(image_path)
            else:
                horario_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                insert_file_process(cnx, cur, horario_atual, image_path, 'processado', 1, 0, 0)
                print("New image processed and saved to DB")

            os.remove(image_path)
            print(f"Removed {filename} from queue.")
        except Exception as e:
            print(f"General error: {e}")
        finally:
            desconectar(cnx, cur)
    return {"message": "Queue images processed successfully"}
