# Novos nomes das tabelas 
- alter table Clientes_Droone rename tbl_clientes;
- alter table Alerta rename tbl_alertas;
- alter table Circuitos rename tbl_circuitos;
- alter table Imagens rename tbl_imagens;
- alter table Feedback rename tbl_feedbacks;
- alter table Estatisticas rename tbl_estatisticas;
- alter table marcas rename tbl_marcas;
- alter table modelos rename tbl_modelos;
- alter table whatsapp rename tbl_whatsapps;
- alter table usermail rename tbl_usermails;
- alter table emails_clientes rename tbl_clientmails;
- alter table enderecos rename tbl_enderecos;
- alter table telefone rename tbl_telefones;
- alter table tokens rename tbl_tokens;
- alter table users rename tbl_users;
- alter table whatsapp_grupos rename tbl_whatsapp_grupos;
- alter table Cameras rename tbl_cameras;
- alter table Clientes_Droone rename tbl_clientes;
  
#  alterações de nome de atributos
## - tbl_circuitos 
- alter table tbl_circuitos rename column IP_principal to ip_principal;
## - tbl_imagens
- alter table tbl_imagens rename column ID_imagens to id_imagem;
- alter table tbl_imagens rename column Timestamp_Criacao to timestamp_create; 
- alter table tbl_imagens rename column Full_Path to `path`; 
- alter table tbl_imagens rename column Data_Hora_Chegada to datetime_chegada; 
- alter table tbl_imagens rename column Data_Hora_Ultima_Mudanca to datetime_ultima_modificacao; 
- alter table tbl_imagens rename column Status_Imagem to `status`;