import telebot
import outputfinal

#plt.plot([1,5,2,6,3], [4,42,3,1,8])
#plt.savefig('graphic.png')


tgtoken = "1040473743:AAFQCePzCbLamT6e3XZCFcTgvk2ekTHTGjQ"
#tgtoken = '1040473743:AAFQCePzCbLamT6e3XZCFcTgvk2ekTHTGjQ'

bot = telebot.TeleBot(tgtoken)

@bot.message_handler(content_types=["text"])
def repmes(message):
    bot.send_message(message.chat.id, outputfinal.parse(message.text))

if __name__ == '__main__':
    bot.polling(none_stop=True)