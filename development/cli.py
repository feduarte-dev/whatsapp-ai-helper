from tools.answer import ai_answer

def cli():
    print("🤖 IA Acolhedora Cristã (digite 'sair' para encerrar)\n")
    while True:
        user_msg = input("Você: ")
        if user_msg.lower() in ["sair", "exit", "quit"]:
            print("IA: Que Deus te abençoe 🙏 Até logo!")
            break

        resposta = ai_answer(user_msg)
        print(f"\nIA: {resposta}\n")

if __name__ == "__main__":
    cli()
