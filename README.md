<!--
    1:1
    1:0..1
    1:N
    1:1..N
    1:0..N
    N:N
    1..N(Supplies):1..N(Supplied by)
    0..N:0..N
-->


Customers
- [PK] customer_id @varchar "Identifier of the customer"
- [FK] region_id "Customer region"
- gender_id @int "Customer gender" ---M(here):1(here)---genders.id
Regions
- id @int "Region identifier"
- name @varchar "Region name"


Genders "Gender fdmflksmdflksdmflksdmlfkdslmfkdslfksdmflkdmsfs kfjngkdfjgndj"
- id @int "Gender identifier"
- name @varchar "Gender name"


Customers.region_id---0..M:1---regions.id
