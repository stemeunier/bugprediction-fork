from statistics import mean

class Math():
    nb_decimal_numbers = 2

    @classmethod
    def get_rounded_mean(cls, values):
        values_mean = mean(values)
        return round(values_mean, cls.nb_decimal_numbers)

    @classmethod
    def get_rounded_rate(cls, value, total):
        rate = (1. * value / total) * 100
        return round(rate, cls.nb_decimal_numbers)
    
    @classmethod
    def get_mean_safe(cls, value):
        if (len(value) > 0):
            return round(mean(value), cls.nb_decimal_numbers)
        return 0