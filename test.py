import mycount

formatted_harry_txt = mycount.format_harry_potter('harry_potter_stein_weisen.txt')
kw_duolingo = mycount.read_known_word_list('duolingo_words_learned.txt')
kw_2000 = mycount.read_known_word_list('german_vocab_2000.txt')
kw_characters = mycount.read_known_word_list('character_names.txt')
all_known_words = list(set(kw_duolingo) | set(kw_2000) | set(kw_characters))
b = mycount.Book(formatted_harry_txt, all_known_words)
