#### Очистка
1. переводим все в нижний регистр
2. удаляем лишние пробелы справа
3. удаление символов \,|,/,",",(,),I,$,&,@,#,*, .
4. удаляем цифры
5. удаляем дубликаты из датасета
6. удаляем путые строки

#### Обогащение
7. заменяем слова
9. разбиваем столбец с профессиями на список слов
8. удаляем суффиксы предлоги
10. все слова переводим в единственное число (from pattern.text.en import singularize)


11. проходим по каждой строке датасета my
12. сравниваем списки слов:
    - если списки равны, то считаем, что название
        профессии введено правильно. задаем lvl:0
    - если списки отличны на 1 слово, то выбираем
        данное назвние за правильную. задаем lvl:1