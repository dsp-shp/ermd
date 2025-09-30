Customers
- [PK] customer_id @varchar "Identifier of the customer"
- [FK] region_id "Customer region"
- gender_id @int "Customer gender" ---M(here):1(here)---genders.id
Regions "asdasd"
- id @int "Region identifier"
- name @varchar "Region name"


Genders "Gender fdmflksmdflksdmflksdmlfkdslmfkdslfksdmflkdmsfs kfjngkdfjgndj"
- id @int "Gender identifier"
- name @varchar "Gender name"


Customers.region_id---0..M:1---regions.id
