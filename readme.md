### Onet-professions

#### финальный файл в result.xlsx, на данный момент 
- 16 - Title
- 22 - Short title
- 190 - Alternate title
- 136 - all (вхождение всех слов из my_name в комбинацию вышеупомянутых столбцов + Element Name)
- 104 - poor accuracy (вхождение слов N-1 из my_name в комбинацию вышеупомянутых столбцов + Element Name)
- 35 - None (неопределено)

#### Очистка

1. переводим все в нижний регистр
2. удаляем лишние пробелы справа
3. удаление символов \,|,",",(,),$,&,@,#,*, .
4. удаляем дубликаты из датасета
5. удаляем путые строки

#### Обогащение

6. разбиваем столбец с профессиями на список слов
7. все слова переводим в единственное число (from pattern.text.en import singularize)


8. проходим по каждой строке датасета my
9. ищем схождение в таком порядке: ['Title', 'Short Title', 'Alternate Title']
10. ищем вхождение всех слов в вышеупомянутые столбцы
