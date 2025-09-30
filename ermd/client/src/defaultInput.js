const defaultInput = `<!--
Инструмент для отрисовки ER-диаграмм на Markdown-like языке.

Рассмотрим работу с ним на примере диаграммы схемы "Снежинки".

Зададим имя, тип и коммент. сущности факта.
-->
fact_sales @table "Таблица фактов"
<!--
Здесь задаем списком атрибуты через "-". Каждая строка состоит:
- наименования атрибута,
- типа,
- ключа/ключей,
- комментария
–-->
- sales_id @INTEGER [PK] "уникальный идентификатор факта продажи"
<!--
Порядок задания параметров произвольный:
–-->
- "ссылка на дату продажи" [FK] @INTEGER date_id
<!--
И все параметры кроме названия атрибута опциональны:
–-->
- quantity
<!--
Прямо здесь же мы можем указать связь
с другим атрибутом другой сущности.

Заметьте, тут отрисовывается отдельная сущность "test_rels" с указанным атрибутом "id", несмотря на то, что далее она нигде явно не задана. Такая сущность получает тип "UNDEFINED" b тип атрибута "UNKNOWN", что говорит о том, что её желательно объявить.

Также оба атрибута автоматически получают по FK ключу.
–-->
- __test_relation "ТЕСТОВЫЙ АТРИБУТ" ---(0:0)---test_rels.id
- product_id @INTEGER "ссылка на продукт"
- customer_id @INTEGER "ссылка на клиента"
- store_id @INTEGER "ссылка на магазин"
- sales_amount @DECIMAL "сумма продажи"

<!--
Далее перечислим все связи:
–-->
* fact_sales.product_id---(0..M:1)---dim_product.product_id
* fact_sales.date_id---(M:1 "Добавим сюда некоторое описание")---dim_date.date_id
* fact_sales.customer_id---1..M:0..1---dim_customer.customer_id
* fact_sales.store_id---M:1---dim_store.store_id

<!--
И зададим измерения:
–-->
@view dim_date "Даты"
- date_id @integer [pk] "уникальный идентификатор даты"
- date @date "фактическая дата"
- day @integer "день месяца"
- month @integer "месяц (число)"
- year @integer "год"

@matview dim_product "Продукты"
- product_id @integer [pk] "уникальный идентификатор продукта"
- product_name @varchar "название продукта"
- category @varchar "категория продукта"

dim_customer "Покупатели"
- customer_id @integer [pk] "уникальный идентификатор покупателя"
- customer_name @varchar "имя покупателя"
- city @varchar "город покупателя"

dim_store "Магазины"
- store_id @integer [pk] "уникальный идентификатор магазина"
- store_name @varchar "название магазина"
- city @varchar "город магазина"`;

export default defaultInput;
