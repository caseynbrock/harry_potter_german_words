import mycount

formatted_harry_txt = mycount.format_harry_potter('harry_potter_stein_weisen.txt')
kw = mycount.read_known_word_list('duolingo_words_learned.txt')
b = mycount.Book(formatted_harry_txt, kw)
