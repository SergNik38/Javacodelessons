class SingletonMeta(type):
    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]


class Singleton(metaclass=SingletonMeta):
    pass


class SingletonNew:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance


class SingletonImport:
    pass


singleton_import_obj = SingletonImport()

if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()
    print(s1 == s2)

    s3 = SingletonNew()
    s4 = SingletonNew()
    print(s3 == s4)

    from singleton import singleton_import_obj as obj1
    from singleton import singleton_import_obj as obj2

    print(obj1 == obj2)
