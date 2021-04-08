class Universities:

    def __init__(self, name, country):
        self.__name = name
        self.__country = country
        self.__rate = []

    @property
    def rate(self):
        return self.__rate

    @rate.setter
    def rate(self, rate):
        for i in range(len(rate)):
            if 1 <= rate[i] <= 100:
                self.__rate.append((rate[i], i))

    def rate_sort(self):
        for i in range(1, len(self.__rate)):
            if self.__rate[i][0] > self.__rate[i - 1][0]:
                self.__rate[i], self.__rate[i - 1] = self.__rate[i - 1], self.__rate[i]

    def rate_print(self, country):
        for i in range(len(self.__rate)):
            if self.__country[i] == country:
                print(self.__name[i])


name = ["first", "second", "third"]
country = ["brazil", "england", "england"]
rate = [59, 98, 93]
un = Universities(name, country)
un.rate = rate
un.rate_sort()
un.rate_print("england")