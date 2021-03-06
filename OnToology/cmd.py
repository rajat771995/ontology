import os
import sys
#################################################################
#           TO make this app compatible with Django             #
#################################################################

from djangoperpmod import *
#
# proj_path = (os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
# print("proj_path: "+proj_path)
# venv_python = os.path.join(proj_path, '.venv', 'bin', 'python')
# # # This is so Django knows where to find stuff.
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OnToology.settings")
# sys.path.append(proj_path)
#
# # This is so my local_settings.py gets loaded.
# os.chdir(proj_path)
#
# # This is so models get loaded.
# from django.core.wsgi import get_wsgi_application
#
# application = get_wsgi_application()

from OnToology.models import *
from OnToology.autoncore import get_ontologies_in_online_repo
from OnToology import settings

from datetime import datetime
from collections import Counter
import json

def llog(msg):
    """
    local log
    :return:
    """
    f = open("alog.log", "a")
    f.write(str(datetime.now()) + " : ")
    f.write(msg)
    f.write("\n")
    f.close()


def get_stats():
    stats = {
        'mean': 0,
        'median': 0,
        'num_of_ontologies': 0,
        'num_of_repos': 0,
        'num_of_pub': 0,
        'num_of_reg_users': 0,
        'onto_per_repo': {
            'data': [],
            'labels': []
        }
    }

    repos = Repo.objects.all()
    ontologies_per_repo = []
    num_corr_repos = 0  # number of repos that has at least one ontology
    for r in repos:
        if '/Curso2017-2018' not in r.url:
            ontos = get_ontologies_in_online_repo(r.url)
            if ontos != []:
                num_of_ontos = len(ontos)
                ontologies_per_repo.append(num_of_ontos)
                num_corr_repos += 1
                if num_of_ontos > 99:
                    msg = "large repo: "+r.url
                    print(msg)
                    llog(msg)

    num_of_ontologies = sum(ontologies_per_repo)
    stats['mean'] = 0
    if num_corr_repos > 0:
        stats['mean'] = num_of_ontologies / num_corr_repos
        ontologies_per_repo.sort()
        # ontologies_per_repo = sorted(ontologies_per_repo)
        if num_corr_repos % 2 == 0:  # even
            print("even")
            idx = (num_corr_repos-1)/2
            print("original idx: ")
            print(idx)
            idx = int(idx)
            print("int idx: %d" % idx)
            stats['median'] = (ontologies_per_repo[idx] + ontologies_per_repo[idx+1]) / 2
        else:
            print("odd")
            idx = num_corr_repos/2
            idx = int(idx)
            print("idx: %d" % idx)
            print("ontologies per repo: ")
            print(ontologies_per_repo)
            stats['median'] = ontologies_per_repo[idx]
    stats['num_of_ontologies'] = num_of_ontologies
    stats['num_of_repos'] = len(repos)
    stats['num_of_pub'] = len(PublishName.objects.all())
    stats['num_of_reg_users'] = len(OUser.objects.all())
    c = Counter(ontologies_per_repo)
    for k in sorted(c.keys()):
        stats['onto_per_repo']['data'].append(c[k])
        stats['onto_per_repo']['labels'].append(k)
    return stats


def update_stats():
    stats = get_stats()
    dt = datetime.now()

    stats_html = """
{%% extends "base2.html"%%}
{%%block body%%}
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js"></script>
    
    generation date: <u>%d-%d-%d</u></br></br>
    The average number of ontologies per repository: %d</br>
    The median number of ontologies per repository: %d</br>
    The total number of ontologies: %d</br>
    The total number of repositories: %d</br>
    The total number of published ontologies: %d</br>
    The total number of registered users: %d</br>
            
    <div class="container-fluid ">
        <div class="row">
            <div class="col-lg-4 col-md-6 col-sm-7 col-xs-10">
                <canvas id="myChart" ></canvas>
            </div>
        </div>
    </div>
    
    <script>
    var data = %s;
    var labels = %s;
    var colors = [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 159, 64)',
        'rgb(153, 102, 255)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        '#4dc9f6',
        '#f67019',
        '#f53794',
        '#537bc4',
        '#acc236',
        '#166a8f',
        '#00a950',
        '#58595b',
        '#8549ba',
    ]

    var ctx = document.getElementById('myChart').getContext('2d');
    var myPieChart = new Chart(ctx,{
          type: 'pie',
            data: {
                datasets: [{
                    label: 'ABC',
                    data: data,
                    backgroundColor: colors
                }],

        // These labels appear in the legend and in the tooltips when hovering different arcs
        labels: labels,

    },
    options: {
    responsive: true,
    legend: {
    position: 'top',
    },
    title: {
    display: true,
    text: 'ontologies per repository'
    },
    animation: {
    animateScale: true,
    animateRotate: true
    }
    }
    });
    </script>
    
    
{%% endblock %%}
    """ % (
        dt.day, dt.month, dt.year,
        stats['mean'],
        stats['median'],
        stats['num_of_ontologies'],
        stats['num_of_repos'],
        stats['num_of_pub'],
        stats['num_of_reg_users'],
        stats['onto_per_repo']['data'],
        stats['onto_per_repo']['labels'],
    )
    stats_dir = os.path.join(settings.BASE_DIR, 'templates', 'stats.html')
    f = open(stats_dir, 'w')
    f.write(stats_html)
    stats_dir = os.path.join(settings.BASE_DIR, 'templates', 'stats.js')
    f = open(stats_dir, 'w')
    f.write("var stats = "+json.dumps(stats))
    f.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'updatestats':
            update_stats()

