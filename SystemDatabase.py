import pymongo
from bson.objectid import ObjectId

# connect to mongodb
myClient = pymongo.MongoClient("mongodb://localhost:27017/")
myDb = myClient["test"]

# link to collection
category = myDb['category']
manufacturers = myDb['manufacturers']
products = myDb['products']
subProducts = myDb['subProducts']

'''
    四种基础数据类型
    1. 产品分类
    2. 产品厂商
    3. 产品型号
    4. 产品系列
    
    此四种基础数据类型按照DataStruct.json文件的格式填写
    存储在本地MongoDB数据库当中
    通过pymongo库进行操作
'''


# 类别
class Category:
    def __init__(self, _name="", _father=None, _info=""):
        if _father is None:
            _father = []
        self.name = _name
        self.father = _father
        self.children = []
        self.info = _info

    # 添加
    def input_category(self):
        self.name = input('请输入类别的名称:')
        father_name = input('请输入父类别的名称(根类别为root,输入0停止输入):')
        while not father_name == '0':
            # 检查父类别是否存在
            if not category.count_documents({'name': father_name}):
                print("父类别不存在,请先创建父类别！")
                return
            else:
                self.father.append(father_name)
            father_name = input('请输入父类别的名称(根类别为root,输入0停止输入):')

        self.info = input('请输入此类别的简介:')
        check = input('请确认您的输入:(1)确认添加;(0)放弃添加')
        if check == '0':
            print("成功放弃添加!")
            return
        # 依次 为 父类别 添加 孩子
        for current_father in self.father:
            category.update_one({'name': current_father}, {"$addToSet": {"children": self.name}})
        # 添加类别
        category.insert_one(self.__dict__)
        print("完成添加!")

    # 通过id删除
    def delete_by_id(self, _id):
        current = category.find_one({'_id': ObjectId(_id)})
        name = current['name']
        father = current['father']
        children = current['children']
        print(name, father)
        category.find_one_and_update({'name': father}, {'$pull': {'children': name}})
        for child in children:
            self.delete_by_id(category.find_one({'name': child})['_id'])
        category.find_one_and_delete({'_id': ObjectId(_id)})

    # 初始化
    @staticmethod
    def init():
        category.drop()
        root = {
            "name": "root",
            "father": [],
            "children": [],
            "info": "根节点",
        }
        category.insert_one(root)

    # 显示所有类别
    def show(self, name='root', depth=0):
        # dfs
        current = category.find_one({'name': name}, {'_id': 0})
        print(depth * '\t', end='')
        for ic in current:
            print(current[ic], end='\t')
        print(category.find_one({'name': name})['_id'])
        children = current['children']
        for child in children:
            self.show(child, depth + 1)


# 厂商
class Manufacture:
    def __init__(self, _name="", _info="", _link=""):
        self.name = _name
        self.info = _info
        self.link = _link

    # 添加
    def input_manufacture(self):
        self.name = input('请输入厂商的名称:')
        self.info = input('请输入厂商的简介:')
        self.link = input('请输入厂商官网地址:')
        check = input('请确认您的输入:(1)确认添加;(0)放弃添加')
        if check == '0':
            print("成功放弃添加!")
            return
        manufacturers.insert_one(self.__dict__)
        print("完成添加!")

    # 通过id删除
    @staticmethod
    def delete_by_id(_id):
        manufacturers.find_one_and_delete({'_id': ObjectId(_id)})

    # TODO 展示厂商包含的产品数量
    # 列出所有厂商
    @staticmethod
    def show():
        for manufacturer in manufacturers.find():
            for i in manufacturer:
                if i == '_id':
                    continue
                print(manufacturer[i], end='\t')
            print(manufacturer['_id'])

    # 清空所有厂商
    @staticmethod
    def init():
        manufacturers.drop()


# 型号
class SubProduct:
    def __init__(self, name="", manufacturer="", origin=None, info="", father=None, required=False, link=""):
        if father is None:
            father = []
        if origin is None:
            origin = []
        self.name = name
        self.manufacturer = manufacturer
        self.origin = origin
        self.info = info
        self.father = father
        self.required = required,
        self.link = link

    # 添加
    def input_sub_product(self):
        self.name = input("请输入该型号的名称:")
        self.manufacturer = input("请输入该型号的厂商名称:")
        if not manufacturers.find_one({'name': self.manufacturer}):
            print('厂商不存在，请先添加厂商')
            return
        self.origin = []
        origin = input("请输入产地(每行一个产地,最后一行只输入一个0,并摁下回车结束输入):\n")
        while not origin == '0':
            self.origin.append(origin)
            origin = input()
        self.info = input("请输入简介:")
        self.required = True if input("请输入该型号是否为必选:(1)是;(0)否:") == '1' else False
        self.link = input("请输入该型号的链接:")
        subProducts.insert_one(self.__dict__)

    # TODO 完善删除：删除型号时删除对应产品系列中的Link

    # 通过id删除
    @staticmethod
    def delete_by_id(_id):
        self = subProducts.find_one({'_id': ObjectId(_id)})
        print(self)
        for father in self['father']:
            father_name = father[0]
            father_type = father[1]
            father_sub_product = products.find_one({'name': father_name})['sub_product']
            print(father_sub_product)
            father_sub_product[father_type].remove(self['name'])
            if not len(father_sub_product[father_type]):
                del father_sub_product[father_type]
            print(father_sub_product)
            print(products.find_one_and_update({'name': father_name}, {'$set': {'sub_product': father_sub_product}}))
        subProducts.find_one_and_delete({'_id': ObjectId(_id)})

    # 初始化
    @staticmethod
    def init():
        subProducts.drop()

    # 显示所有型号
    @staticmethod
    def show():
        for subProduct in subProducts.find().sort([("name", 1)]):
            for i in subProduct:
                if i == '_id':
                    continue
                print(subProduct[i], end='\t')
            print(subProduct['_id'])


# 产品系列
class Product:
    def __init__(self, _name="", _manufacturer="", _origin=None, _info="", _category=None, _sub_product=None, _link=""):
        if _origin is None:
            _origin = []
        if _category is None:
            _category = []
        if _sub_product is None:
            _sub_product = {}
        self.name = _name
        self.manufacturer = _manufacturer
        self.origin = _origin
        self.info = _info
        self.category = _category
        self.sub_product = _sub_product
        self.link = _link

    # 添加
    def input_product(self):
        self.name = input("请输入该产品系列的名称:")
        self.manufacturer = input("请输入该产品系列的厂商名称:")
        if not manufacturers.find_one({'name': self.manufacturer}):
            print('厂商不存在，请先添加厂商')
            return
        self.origin = []
        origin = input("请输入产地(每行一个产地,最后一行只输入一个0,并摁下回车结束输入):\n")
        while not origin == '0':
            self.origin.append(origin)
            origin = input()
        self.category = []
        current_category = input("请输入产品直属最底层类别(每行一个类别,最后一行只输入一个0,并摁下回车结束输入):\n")
        while not current_category == '0':
            if not category.find_one({'name': current_category}):
                print("此分类不存在，请先添加类别")
                current_category = input("请输入产品直属最底层类别(每行一个类别,最后一行只输入一个0,并摁下回车结束输入):\n")
                continue
            self.category.append(current_category)
            current_category = input()

        sub_flag = input('请输入该产品系列包含的型号类别名称(输入0并摁下回车结束添加):')
        while not sub_flag == '0':
            if sub_flag not in self.sub_product:
                self.sub_product[sub_flag] = []
            sub_product_id = input('请输入此类别型号的id(输入0并摁下回车结束添加):')
            while not sub_product_id == '0':
                if not subProducts.find_one({'_id': ObjectId(sub_product_id)}):
                    print('您输入的id不存在，请先添加型号')

                else:
                    sub_product_name = subProducts.find_one({'_id': ObjectId(sub_product_id)})['name']
                    self.sub_product[sub_flag].append(sub_product_name)
                    subProducts.find_one_and_update({'_id': ObjectId(sub_product_id)},
                                                    {'$addToSet': {'father': [self.name, sub_flag]}})
                sub_product_id = input('请输入此类别型号的id(输入0并摁下回车结束添加):')
            sub_flag = input('请输入该产品系列包含的型号类别名称(输入0并摁下回车结束添加):')
        self.info = input("请输入简介:")
        self.link = input("请输入该产品的链接:")
        self.insert()

    # 插入
    def insert(self):
        products.insert_one(self.__dict__)

    # TODO 完善删除：删除产品系列时删除对应产品系列中的Link
    # 通过id删除
    @staticmethod
    def delete_by_id(_id):
        products.find_one_and_delete({'_id': ObjectId(_id)})

    # 初始化
    @staticmethod
    def init():
        products.drop()

    # 显示所有型号
    @staticmethod
    def show():
        conditions = {"category": {'$in': []}, "manufacturer": ""}
        while True:
            cond_flag = input('请输入新增筛选类型:(1)产品类别(2)产品厂商(0)结束输入\n')
            if cond_flag == '1':
                current_category = input('请输入产品类别名称:')
                if not category.find_one({'name': current_category}):
                    print('您输入的类别不存在，请先添加类别')
                else:
                    # bfs 添加当前类别的所有子类别
                    current = category.find_one({'name': current_category})
                    bfs = [current]
                    while len(bfs):
                        current = bfs[0]
                        conditions['category']['$in'].append(current['name'])
                        bfs.pop(0)
                        for child in current['children']:
                            bfs.append(category.find_one({'name': child}))

            elif cond_flag == '2':
                current_manufacturer = input('请输入产品厂商名称:')
                if not manufacturers.find_one({'name': current_manufacturer}):
                    print('您输入的厂商不存在，请先添加厂商')
                else:
                    conditions['manufacturer'] = current_manufacturer

            elif cond_flag == '0':
                break

            else:
                print("错误的输入")
        if not conditions['manufacturer']:
            conditions.pop('manufacturer')
        if not len(conditions['category']['$in']):
            conditions.pop('category')
        print(conditions)
        for product in products.find(conditions).sort([("name", 1)]):
            for i in product:
                if i == '_id':
                    continue
                print(product[i], end='\t')
            print(product['_id'])


'''
    操作:
        1. 添加
        2. 删除
        3. 查询
        4. 修改
'''


# 添加
def add_element():
    add_mode = input('请输入想要添加的类型:(1)类别;(2)型号;(3)产品系列;(4)厂商:\n')
    # 添加类别
    if add_mode == '1':
        x = Category()
        x.input_category()
        del x

    elif add_mode == '2':
        x = SubProduct()
        x.input_sub_product()
        del x

    elif add_mode == '3':
        x = Product()
        x.input_product()
        del x

    elif add_mode == '4':
        x = Manufacture()
        x.input_manufacture()
        del x

    else:
        print("错误的输入")


# 删除
def del_element():
    del_mode = input('请输入想要删除的类型:(1)类别;(2)型号;(3)产品系列;(4)厂商:\n')
    # 添加类别
    if del_mode == '1':
        x = Category()
        x.delete_by_id(input('请输入需要删除的类型的id:'))
        del x

    elif del_mode == '2':
        x = SubProduct()
        x.delete_by_id(input('请输入需要删除的型号的id:'))
        del x

    elif del_mode == '3':
        x = Product()
        x.delete_by_id(input('请输入需要删除的产品系列的id:'))
        del x

    elif del_mode == '4':
        x = Manufacture()
        x.delete_by_id(input('请输入需要删除的厂商的id:'))
        del x

    else:
        print("错误的输入")


# 查询
def show_element():
    add_mode = input('请输入想要查询的类型:(1)显示所有类型;(2)查询指定产品系列;(3)显示所有产品型号;(4)显示所有厂商\n')
    # 展示所有类别
    if add_mode == '1':
        x = Category()
        x.show()
        del x

    elif add_mode == '2':
        x = Product()
        x.show()
        del x

    # 展示所有型号
    elif add_mode == '3':
        x = SubProduct()
        x.show()
        del x

    # 展示所有厂商
    elif add_mode == '4':
        x = Manufacture()
        x.show()
        del x

    else:
        print("错误的输入")


if __name__ == '__main__':
    while True:
        print("欢迎使用!输入数字并按下回车以继续。")
        mode = input("(1)添加(2)删除(3)查询(4)修改(5)初始化(0)退出\n")
        if mode == '1':
            add_element()

        elif mode == '2':
            del_element()

        elif mode == '3':
            show_element()

        elif mode == '4':
            continue
        elif mode == '5':
            # 分类初始化
            _c = Category()
            _c.init()
            del _c
            # 厂商初始化
            _m = Manufacture()
            _m.init()
            del _m
            # 型号初始化
            _s = SubProduct()
            _s.init()
            del _s
            # 产品系列初始化
            _p = Product()
            _p.init()
            del _p

        elif mode == '0':
            break

        else:
            print("错误的输入")
