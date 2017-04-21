from django.shortcuts import render

from graphos.renderers.gchart import LineChart
from graphos.sources.simple import SimpleDataSource

from .models import Stats, Video


def home(request):
    if request.is_ajax():
        target = 'ajax/ajax_home.html'
    else:
        target = 'home.html'
    context = {}
    context['videos'] = Video.objects.all()
    videos = Video.objects.all().order_by('id')
    context['offset_id'] = -(videos[0].id - 1) if videos else 0
    return render(request, target, context)


def getChart():
    data = [['#', 'time'], [0, 0]]

    stat_recs = Stats.objects.all()
    counter = 0
    s = 0
    for rec in stat_recs:
        counter += 1
        time = (float(rec.consume_time) - float(rec.enque_time))
        s += time
        data.append([counter, time])

    # DataSource object
    data_source = SimpleDataSource(data=data)
    # Chart object
    option_dic = {'hAxis': {'title': 'messages'},
                  'title': 'Message Consumption Time Monitoring',
                  'vAxis': {'title': 'consumption time(s)'}}
    chart = LineChart(data_source, options=option_dic, width=1000)
    return {'chart': chart}, counter, s


def getStats(count, s):
    context = {}

    latest = Stats.objects.all().order_by('-id')
    if latest:
        latest = latest[0]
        context['consumptionTime'] = (float(latest.consume_time) - float(latest.enque_time))
    else:
        context['consumptionTime'] = "UNKOWN"
    if count:
        context['avg_consumptionTime'] = s / count
    else:
        context['avg_consumptionTime'] = "UNKOWN"
    return context


def stats(request):
    context, counter, s = getChart()
    context.update(getStats(counter, s))
    return render(request, 'stats.html', context)


def update_charts(request):
    context, counter, s = getChart()
    return render(request, 'ajax/ajax_charts.html', context)


def update_stats(request):
    _, counter, s = getChart()
    context = getStats(counter, s)
    return render(request, 'ajax/ajax_stats.html', context)
