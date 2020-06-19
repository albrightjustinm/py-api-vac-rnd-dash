import logging
import pycountry

tlogg = logging.getLogger('.'.join(['api.app', __name__.strip('api.')]))



def _split_country_string(s):
    countries_a = s.split(',')
    countries_b = []
    
    for country in countries_a:
        # Business Rule: city - country
        if country is not None:
            countries_b.append(country.split('-')[-1])
    
    return countries_b


def _remove_null_names(s):
    default_names = ['na', 'n/a', '']
    return [name for name in s if name.strip().lower() not in default_names]

def clean_country(country_names: str) -> str:
    result = []

    countries = _split_country_string(country_names)

    countries = _remove_null_names(countries)

    for country in countries:
        try:
            if country is None or len(country) < 2:
                pass
            else:
                curr_country = pycountry.countries.search_fuzzy(country.strip())
                result.append(curr_country[0].alpha_3)
        except LookupError:
            pass
        except Exception as e:
            tlogg.error(f"Error in country standardization {e}")
    if len(result) == 0:
        return None
    return ",".join(result)


def clean_lists(x:str) -> str:
    if x is None:
        return None 

    if "," in x:
        temp_list = x.split(",")
    elif ";" in x:
        temp_list = x.split(";")
    else:
        return x

    def clean_list_item(item: str = None):
        assert type(item) == str
        temp_item = item
        temp_item = temp_item.strip()
        temp_item = temp_item.replace('"', "")
        return temp_item

    return ",".join([clean_list_item(item) for item in temp_list])


def lower(x):
    """
    Lowers capitalization of all observations in a given str type column.
    """
    try:
        return x.lower()
    except:
        return x