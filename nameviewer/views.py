from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from orders.models import Forename, Surname

from . import helpers

# Create your views here.
@login_required
def index(request):
    """
    Allow a logged in user to generate name variations for a first and/or last name
    :param request:
    :return:
    """

    name_to_search = request.GET.get('name','lloyd') # may want to set default param too
    # print('Name: {}'.format(type(name_to_search)))
    name_type = request.GET.get('rad')

    forename_namematch_list = []
    surname_namematch_list = []
    name_combinations = []

    second_name_to_search = request.GET.get('second_name')
    if second_name_to_search:
        name_filter = helpers.get_forename_results(request, name_to_search) # @TODO: cleanup unused call

        forename_filter = name_filter
        for fn in forename_filter.qs:
            forename_namematch_list.append(fn.name_match)

        # surname_filter = _get_surname_results(request, second_name_to_search)
        surname_list = Surname.objects.filter(name=second_name_to_search)
        # surname_filter = SurnameFilter(request.GET, queryset=surname_list)

        for sn in surname_list:
            surname_namematch_list.append(sn.name_match)
        print(('Lists count: forename {}, surname {}'.format(len(forename_namematch_list), len(surname_list))))

        # name_combinations = _make_name_combinations(forename_namematch_list, surname_namematch_list)
        name_combinations = helpers.make_name_combinations(forename_namematch_list, surname_namematch_list)
        # import itertools
        # name_combinations = list(itertools.product(forename_namematch_list, surname_namematch_list))
    else:
        if name_type == 'forename':
            name_filter = helpers.get_forename_results(request, name_to_search)
        else:
            name_filter = helpers.get_surname_results(request, name_to_search)

    context = {
        'filter': name_filter,
        'rad': name_type,
        'matched_forenames': forename_namematch_list,
        'matched_surnames': surname_namematch_list,
        'name_combinations': name_combinations,
        'num_name_combs': len(name_combinations),
    }
    return render(request, 'nameviewer/index.html', context)

@login_required
def common_names(request, name_type=None, name_select=None):
    """
    Display a view with a list of common names for either surnames or forenames
    :param request: the http request object
    :param name_type: the type of view to return based on surname or forename
    :param name_select: the name to use for the lookup
    :return:
    """
    from django.conf import settings
    from nameviewer.helpers import get_name_match_score
    from nameviewer.utils import NameAliasUtils
    from orders.models import Surname, Forename

    if request.method == "POST":
        # process new alias preferences
        all_name_var_objs = NameAliasUtils.load_scored_names(name_select, name_type)
        all_name_variations = set([x.name_match for x in all_name_var_objs])
        active_name_variations = request.POST.getlist('name-variation-select[]')
        inactive_name_variations = list(all_name_variations - set(active_name_variations))
        if name_type == 'surname':
            Surname.objects.using(settings.NAMESEARCH_DB).filter(name=name_select.lower()).filter(name_match__in=active_name_variations).update(deleted='')
            Surname.objects.using(settings.NAMESEARCH_DB).filter(name=name_select.lower()).filter(name_match__in=inactive_name_variations).update(deleted='Y')
        else:
            Forename.objects.using(settings.NAMESEARCH_DB).filter(name=name_select.lower()).filter(name_match__in=active_name_variations).update(deleted='N')
            Forename.objects.using(settings.NAMESEARCH_DB).filter(name=name_select.lower()).filter(name_match__in=inactive_name_variations).update(deleted='Y')

    names_list, scored_names = NameAliasUtils.load_common_names(name_type, name_select)
    if name_type == 'surname':
        name_match_score = int(get_name_match_score())
    else:
        name_match_score = int(get_name_match_score('FIRST_NAME'))
    context = {
        'common_names_list': names_list,
        'name_type': name_type,
        'name_select': name_select,
        'scored_names': scored_names,
        'score_threshold': name_match_score  # 'FIRST_NAME
    }
    return render(request, 'nameviewer/common_names.html', context)

@login_required
def new_name_alias(request, name_type=None, name_select=None, new_name_alias=None):
    """
    View to add a new name to the alias dictionary
    :param request: the request object
    :param name_type: type of name to add
    :param name_select: the base name to use for adding the new alias
    :param new_name_alias: the new alias to add to the base name
    :return:
    """
    from nameviewer.utils import NameAliasUtils

    NameAliasUtils.add_new_alias(name_type, name_select, new_name_alias)
    return common_names(request, name_type, name_select)
