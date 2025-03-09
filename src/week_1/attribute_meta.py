import datetime


class AttributeMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs["created_at"] = datetime.datetime.now()
        return super().__new__(mcs, name, bases, attrs)


class Example(metaclass=AttributeMeta):
    pass


if __name__ == "__main__":
    example = Example()
    print(example.created_at)
