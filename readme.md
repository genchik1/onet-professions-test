### Onet-professions

#### финальный файл в result.xlsx, на данный момент 366 совпадений

#### Очистка

1. переводим все в нижний регистр
2. удаляем лишние пробелы справа
3. удаление символов \,|,/,",",(,),$,&,@,#,*, .
4. удаляем цифры
5. удаляем дубликаты из датасета
6. удаляем путые строки

#### Обогащение

7. разбиваем столбец с профессиями на список слов
8. все слова переводим в единственное число (from pattern.text.en import singularize)


9. проходим по каждой строке датасета my
10. ищем схождение в таком порядке: ['Title', 'Short Title', 'Alternate Title']
11. ищем вхождение всех слов в вышеупомянутые столбцы
