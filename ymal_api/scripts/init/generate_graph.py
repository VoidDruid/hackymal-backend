import csv

from dataplane import neo4j
from scripts.utils import info, title


def format_q(q):
    return q


SYMBOLS = (
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
    "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA",
)
tr = {ord(a): ord(b) for a, b in zip(*SYMBOLS)}


def _graph_name(name: str):
    return name.translate(tr).replace("-", "_").replace(" ", "")


def consumer_name(name: str):
    return _graph_name(name) + "_c"


def point_name(name: str):
    return _graph_name(name) + "_p"


def main() -> None:
    print(title("River graph"))
    print(info("Generating path graph"))

    def generator(tx):
        distance_matrix = {}
        with open("/etc/gis/distance_matrix.csv", newline="") as matrix_csv:
            reader = csv.DictReader(matrix_csv)
            for row in reader:
                distance_matrix[row["ID"]] = {k: v for k, v in row.items() if k != "ID"}

        def convert_dist(distance_raw):
            return round(float(distance_raw) / 1000, 3)

        translit_map = {
            "Pitlar": "Pitlyar",
            "Suryskary": "Shurishakri",
            "Vosahovo": "Vosyahovo",
            "Muji": "Muzhi",
            "ObKatravozh": "ObKatrovozh",
            "Azovy": "Azovi",
            "Katravoj": "Katrovozh",
            "ZelenyjAr": "ZeleniyYar",
            "Labytnangi": "Labytnagi",
            "Harsajm": "Harsaim",
            "Beloarsk": "Beloyarsk",
            "Suc_e": "Schuchie",
            "ObKutopygan": "ObKutopugan",
            "Kutop_ugan": "Kutopugan",
            "Ar_Sale": "YarSale",
            "NovyjPort": "NewPort",
            "MysKamennyj": "MysKamenniy",
            "Se_Aha": "Seyaha",
        }

        def path_command(point1, point2, traversal="any"):
            def preprocess_name(p_name):
                if p_name.endswith("_p"):
                    p_name = p_name[:-2]
                return translit_map.get(p_name, p_name)

            point1_search = preprocess_name(point1)
            point2_search = preprocess_name(point2)

            distance = convert_dist(distance_matrix[point1_search][point2_search])
            return f'CREATE ({point1})-[:Path {{weight:{distance}, traversal: "{traversal}"}}]->({point2})'

        consumers_set = {
            "Антипаюта",
            "Нори",
            "Яр-Сале",
            "Се-Яха",
            "Питляр",
            "Самбург",
            "Восяхово",
            "Шурышкары",
            "Салемал",
            "Ныда",
            "Горки",
            "Кутопьюган",
            "Находка",
            "Овгорт",
            "Лабытнанги",
            "Мыс Каменный",
            "Мужи",
            "Белоярск",
            "Зеленый Яр",
            "Салехард",
            "Аксарка",
            "Щучье",
            "Катравож",
            "Лопхари",
            "Харсайм",
            "Азовы",
            "Панаевск",
            "Новый Порт",
        }

        current_id = 0

        def next_id():
            nonlocal current_id
            current_id += 1
            return current_id

        # 'name': (consumer_id, point_id)
        consumers_and_points = {name: (next_id(), next_id()) for name in consumers_set}

        consumers_query = ""
        for consumer_name_ in consumers_and_points:
            consumer_id, point_id = consumers_and_points[consumer_name_]
            consumer_tr_name = consumer_name(consumer_name_)
            point_tr_name = point_name(consumer_name_)
            consumers_query += f'CREATE ({consumer_tr_name}:Consumer {{id: {consumer_id}, name:"{consumer_name_}"}})\n'
            consumers_query += f'CREATE ({point_tr_name}:Point {{id: {point_id}, name:"Причал {consumer_name_}"}})\n'
            consumers_query += f'CREATE ({point_tr_name})-[:Path {{weight:0, traversal: "any"}}]->({consumer_tr_name})\n'

        tx_return = tx.run(
            consumers_query
            + f"""
        CREATE (ObLophari:Point {{id:{next_id()}, name:"Обь-Лопхари"}})
        {path_command('ObLophari', point_name('Лопхари'))}
        {path_command('ObLophari', point_name('Горки'))}
        
        {path_command(point_name('Горки'), point_name('Питляр'))}
        
        CREATE (ObPitlyar:Point {{id:{next_id()}, name:"Обь-Питляр"}})
        {path_command(point_name('Питляр'), 'ObPitlyar')}
        {path_command('ObPitlyar', point_name('Шурышкары'), 'small')}

        CREATE (ObVosyahovo:Point {{id:{next_id()}, name:"Обь-Восяхово"}})
        {path_command(point_name('Шурышкары'), 'ObVosyahovo', 'small')}
        {path_command('ObVosyahovo', point_name('Восяхово'), 'small')}
        {path_command('ObVosyahovo', point_name('Мужи'), 'small')}
        
        CREATE (ObMuzhi:Point {{id:{next_id()}, name:"Обь-Мужи"}})
        {path_command(point_name('Мужи'), 'ObMuzhi', 'small')}
        {path_command('ObMuzhi', point_name('Азовы'), 'small')}
        {path_command('ObMuzhi', point_name('Овгорт'), 'small')}
        
        CREATE (ObKatravozh:Point {{id:{next_id()}, name:"Обь-Катравож"}})
        {path_command('ObPitlyar', 'ObKatravozh')}
        {path_command('ObKatravozh', point_name('Катравож'), 'small')}
        {path_command('ObKatravozh', point_name('Салехард'))}
        
        {path_command(point_name('Салехард'), point_name('Зеленый Яр'), 'small')}
        {path_command(point_name('Салехард'), point_name('Лабытнанги'))}
        {path_command(point_name('Лабытнанги'), point_name('Харсайм'))}
        
        CREATE (ObBeloyarsk:Point {{id:{next_id()}, name:"Обь-Белоярск"}})
        {path_command(point_name('Харсайм'), 'ObBeloyarsk',)}
        {path_command('ObBeloyarsk', point_name('Белоярск'), 'small')}
        {path_command('ObBeloyarsk', point_name('Аксарка'))}
        
        {path_command(point_name('Белоярск'), point_name('Щучье'), 'small')}
        
        CREATE (ObBeloyarsk_2:Point {{id:{next_id()}, name:"Обь-Белоярск 2"}})
        {path_command(point_name('Аксарка'), 'ObBeloyarsk_2',)}
        {path_command(point_name('Белоярск'), 'ObBeloyarsk_2', 'small')}
        {path_command('ObBeloyarsk_2', point_name('Щучье'), 'small')}
        {path_command('ObBeloyarsk_2', point_name('Салемал'))}
        
        CREATE (ObKutopygan:Point {{id:{next_id()}, name:"Обь-Кутопьюган"}})
        {path_command(point_name('Салемал'), 'ObKutopygan')}
        {path_command('ObKutopygan', point_name('Кутопьюган'))}
        
        CREATE (ObYarSale:Point {{id:{next_id()}, name:"Обь-Яр-Сале"}})
        {path_command('ObKutopygan', 'ObYarSale',)}
        {path_command('ObYarSale', point_name('Панаевск'))}
        {path_command('ObYarSale', point_name('Яр-Сале'), 'small')}
        
        {path_command(point_name('Кутопьюган'), point_name('Нори'))}
        
        CREATE (ObNyda:Point {{id:{next_id()}, name:"Обь-Ныда"}})
        {path_command(point_name('Нори'), 'ObNyda')}
        {path_command(point_name('Кутопьюган'), 'ObNyda')}
        {path_command('ObNyda', point_name('Ныда'))}
        {path_command('ObNyda', point_name('Новый Порт'))}
        
        CREATE (ObYarSale_2:Point {{id:{next_id()}, name:"Обь-Яр-Сале-2"}})
        {path_command(point_name('Яр-Сале'), 'ObYarSale_2')}
        {path_command('ObYarSale_2', 'ObNyda')}
        
        {path_command(point_name('Новый Порт'), point_name('Мыс Каменный'))}
        
        CREATE (ObAntipauta:Point {{id:{next_id()}, name:"Обь-Антипаюта"}})
        {path_command(point_name('Мыс Каменный'), 'ObAntipauta')}
        {path_command('ObAntipauta', point_name('Антипаюта'))}
        
        CREATE (ObSeyaha:Point {{id:{next_id()}, name:"Обь-Се-Яха"}})
        {path_command('ObAntipauta', 'ObSeyaha')}
        {path_command('ObSeyaha', point_name('Се-Яха'), 'small')}
        
        {path_command(point_name('Антипаюта'), point_name('Находка'), 'small')}
        {path_command(point_name('Находка'), point_name('Самбург'))}
        """
        )
        return tx_return.single()

    neo4j.run_sync(generator)

    print("Successfully generated everything")


if __name__ == "__main__":
    raise RuntimeError("Do not run scripts directly!")
