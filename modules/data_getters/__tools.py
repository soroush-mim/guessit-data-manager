def money_value(money):
    """ change the number of money to a standard form """

    return int(
        float(money[1:-1]) * (10 ** (3 if money[-1] == 'K' else
                                     6 if money[-1] == 'M' else 0))) if money != '€0' else 0


def date_value(date):
    """
    get the standard type of date

    :param date:
    :return: tumple
    """

    months = \
        {'January'      : 1,  'February': 2, 'March'	    : 3,
         'April'		: 4 , 'May'		: 5	, 'June'		: 6,
         'July'		    : 7 , 'August'	: 8	, 'September'	: 9,
         'October'	    : 10, 'November': 11, 'December'	: 12}

    return (int(date[-4:]),
            int([value for key, value in months.items() if date[:3] in key][0]),
            int(date[date.find(' ') + 1: date.find(',')]))
