from botcity.core import DesktopBot


class DrooneSend(DesktopBot):

    def send_message(self, telefone, mensagem):
        # abre o WhatsApp Web
        self.browse('https://web.whatsapp.com/')

        # verifica se o WhatsApp realmente abriu
        if not self.find("new_conversation",
                         matching=0.80,
                         waiting_time=10000,
                         grayscale=True):
            print("Não encontrei: new_conversation")
        self.click()

        # digita o número do contato
        if not self.find(
                "input_number", matching=0.80, waiting_time=10000,
                grayscale=True):
            print("Não encontrei: input_number")
        self.paste(text=telefone)
        self.wait(2000)
        self.enter()

        # digita a mensagem
        if not self.find("input_mensagem",
                         matching=0.80,
                         waiting_time=15000,
                         grayscale=True):
            print("Não encontrei: input_mensagem")
            self.alt_f4(2000)
            print('Verifique se o número realmente existe')
        else:
            self.paste(text=mensagem, wait=2000)

            # aperta no botão de enviar
            if not self.find("send_mensagem",
                             matching=0.97,
                             waiting_time=10000,
                             grayscale=True):
                print("Não encontrei: send_mensagem")
            self.click()

            # verifica se já enviou
            if not self.find("verify_menssage",
                             matching=0.97,
                             waiting_time=10000,
                             grayscale=True):
                print("Não encontrei: verify_menssage")
                self.alt_f4()
            else:
                self.alt_f4()


if __name__ == '__main__':
    Bot = DrooneSend()
    telefone = '1999872472'
    Bot.send_message(telefone, 'teste')
