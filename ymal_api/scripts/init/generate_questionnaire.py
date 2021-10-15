from dataplane import neo4j
from scripts.utils import info, title


def format_q(q):
    return q

SYMBOLS = (
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
    "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA"
)
tr = {ord(a): ord(b) for a, b in zip(*SYMBOLS)}


def consumer_name(name: str):
    return name.translate(tr).replace('-', '_') + '_c'


def point_name(name: str):
    return name.translate(tr).replace('-', '_') + '_p'


def main() -> None:
    print(info("Generating path graph"))

    def generator(tx):
        consumers_set = {
            'Антипаюта', 'Нори', 'Красноселькуп', 'Яр-Сале', 'Се-Яха', 'Питляр', 'Самбург', 'Восяхово', 'Шурышкары',
            'Салемал', 'Ныда', 'Горки', 'Кутопьюган', 'Находка', 'Овгорт', 'Лабытнанги', 'Мыс Каменный', 'Мужи',
            'Белоярск', 'Гыда', 'Зеленый Яр', 'Салехард', 'Аксарка', 'Щучье', 'Катравож', 'Лопхари', 'Харсайм',
            'Антипаюта, Гыда', 'Халясавей', 'Сюнай Сале', 'Азовы', 'Панаевск', 'Новый Порт', 'Толька'
        }
        points = [
            'ObLophari', 'Gorki', 'Azovi', 'Ovgort', 'Muzhi', 'Shurishakri', 'Pitlyar', 'ObPitlyar', 'Katrovozh',
            'ObKatrovozh', 'Salehard', 'Labytnagi', 'Harsaim', 'Aksarka', 'Beloyarsk', 'ObBeloyarsk', 'Salemal',
            'ObBeloyarsk_2', 'Panaevsk', 'Kutopugan', 'ObKutopugan', 'YarSale', 'ObYarSale', 'Nyda', 'ObYarSale_2',
            'NewPort', 'ObNyda', 'MysKamenniy', 'Nahodka', 'Antipauta', 'ObAntipauta',
            'ObMuzhi', 'Schuchie', 'ZeleniyYar', 'Samburg'
        ]

        current_id = 0

        def next_id():
            nonlocal current_id
            current_id += 1
            return current_id

        # 'name': (consumer_id, point_id)
        consumers_and_points = {name: (next_id(), next_id()) for name in consumers_set}

        consumers_query = ''
        for consumer_name_ in consumers_and_points:
            consumer_id, point_id = consumers_and_points[consumer_name_]
            consumer_tr_name = consumer_name(consumer_name_)
            point_tr_name = point_name(consumer_name_)
            consumers_query += \
                f'CREATE ({consumer_tr_name}:Consumer {{id: {consumer_id}, name:"{consumer_name_}"}})'
            consumers_query += \
                f'CREATE ({point_tr_name}:Point {{id: {point_id}}})'
            consumers_query += f'CREATE ({point_tr_name})-[:Path {{weight:0, traversal: "any"}}]->({consumer_tr_name})'

        tx_return = tx.run(
            consumers_query + f"""
        CREATE (Zavod111:Producer {{id:1, name:"Такой-то завод", type:"type", amount:100}})
        
        CREATE (ObLophari:Point {{id:{next_id()}}})
        CREATE ({point_name('Лопхари')})-[:Path {{weight:0, traversal: "any"}}]->(ObLophari)
        CREATE (ObLophari)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Горки')})
        
        CREATE ({point_name('Горки')})-[:Path {{weight:0, traversal: "any"}}]->({point_name('Питляр')})
        
        CREATE (ObPitlyar:Point {{id:{next_id()}}})
        CREATE ({point_name('Питляр')})-[:Path {{weight:0, traversal: "any"}}]->(ObPitlyar)
        CREATE (ObPitlyar)-[:Path {{weight:0, traversal: "small"}}]->({point_name('Шурышкары')})

        CREATE ({point_name('Шурышкары')})-[:Path {{weight:0, traversal: "small"}}]->({point_name('Мужи')})
        
        CREATE (ObMuzhi:Point {{id:{next_id()}}})
        CREATE ({point_name('Мужи')})-[:Path {{weight:0, traversal: "small"}}]->(ObMuzhi)
        CREATE (ObMuzhi)-[:Path {{weight:0, traversal: "small"}}]->({point_name('Азовы')})
        CREATE (ObMuzhi)-[:Path {{weight:0, traversal: "small"}}]->({point_name('Овгорт')})
        
        CREATE (ObKatravozh:Point {{id:{next_id()}}})
        CREATE (ObPitlyar)-[:Path {{weight:0, traversal: "any"}}]->(ObKatravozh)
        CREATE (ObKatravozh)-[:Path {{weight:0, traversal: "small"}}]->({point_name('Катравож')})
        CREATE (ObKatravozh)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Салехард')})
        
        CREATE ({point_name('Салехард')})-[:Path {{weight:0, traversal: "small"}}]->({point_name('Зеленый Яр')})
        CREATE ({point_name('Салехард')})-[:Path {{weight:0, traversal: "any"}}]->({point_name('Лабытнанги')})
        CREATE ({point_name('Лабытнанги')})-[:Path {{weight:0, traversal: "any"}}]->({point_name('Харсайм')})
        
        CREATE (ObBeloyarsk:Point {{id:{next_id()}}})
        CREATE ({point_name('Харсайм')})-[:Path {{weight:0, traversal: "any"}}]->(ObBeloyarsk)
        CREATE (ObBeloyarsk)-[:Path {{weight:0, traversal: "small"}}]->({point_name('Белоярск')})
        CREATE (ObBeloyarsk)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Аксарка')})
        
        CREATE ({point_name('Белоярск')})-[:Path {{weight:0, traversal: "small"}}]->({point_name('Щучье')})
        
        CREATE (ObBeloyarsk_2:Point {{id:{next_id()}}})
        CREATE ({point_name('Аксарка')})-[:Path {{weight:0, traversal: "any"}}]->(ObBeloyarsk_2)
        CREATE ({point_name('Белоярск')})-[:Path {{weight:0, traversal: "small"}}]->(ObBeloyarsk_2)
        CREATE (ObBeloyarsk_2)-[:Path {{weight:0, traversal: "small"}}]->({point_name('Щучье')})
        CREATE (ObBeloyarsk_2)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Салемал')})
        
        CREATE (ObKutopygan:Point {{id:{next_id()}}})
        CREATE ({point_name('Салемал')})-[:Path {{weight:0, traversal: "any"}}]->(ObKutopygan)
        CREATE (ObKutopygan)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Кутопьюган')})
        
        CREATE (ObYarSale:Point {{id:{next_id()}}})
        CREATE (ObKutopygan)-[:Path {{weight:0, traversal: "any"}}]->(ObYarSale)
        CREATE (ObYarSale)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Панаевск')})
        CREATE (ObYarSale)-[:Path {{weight:0, traversal: "small"}}]->({point_name('Яр-Сале')})
        
        CREATE (ObNyda:Point {{id:{next_id()}}})
        CREATE ({point_name('Кутопьюган')})-[:Path {{weight:0, traversal: "any"}}]->(ObNyda)
        CREATE (ObNyda)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Ныда')})
        CREATE (ObNyda)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Новый Порт')})
        
        CREATE (ObYarSale_2:Point {{id:{next_id()}}})
        CREATE ({point_name('Яр-Сале')})-[:Path {{weight:0, traversal: "any"}}]->(ObYarSale_2)
        
        CREATE ({point_name('Новый Порт')})-[:Path {{weight:0, traversal: "any"}}]->({point_name('Мыс Каменный')})
        
        CREATE (ObAntipauta:Point {{id:{next_id()}}})
        CREATE ({point_name('Мыс Каменный')})-[:Path {{weight:0, traversal: "any"}}]->(ObAntipauta)
        CREATE (ObAntipauta)-[:Path {{weight:0, traversal: "any"}}]->({point_name('Антипаюта')})
        
        CREATE ({point_name('Антипаюта')})-[:Path {{weight:0, traversal: "small"}}]->({point_name('Находка')})
        CREATE ({point_name('Находка')})-[:Path {{weight:0, traversal: "any"}}]->({point_name('Самбург')})
        """
        )
        return tx_return.single()

    neo4j.run_sync(generator)

    print("Successfully generated everything")


if __name__ == "__main__":
    raise RuntimeError("Do not run scripts directly!")
