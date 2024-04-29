import json
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat

from datetime import datetime

from django.views import View
from collections import defaultdict
import time
from lab_results_backend_db.mouse import mouse_id_map, TUMOR_MAP
import math
from django.http import JsonResponse, HttpRequest
from lab_results_backend_db.models import TumorVolume, IvisData, Pilot, Group, Mouse
import pandas as pd
from django.views.decorators.csrf import csrf_exempt


class Tumor(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        # Assuming pilot_id is passed as a query parameter
        pilot_id = request.GET.get('pilot_id')
        # Assuming group_ids is passed as a query parameter
        group_ids = request.GET.getlist('group_id[]')

        # Filter tumor volumes based on pilot_id and group_ids
        tumor_volumes = TumorVolume.objects.filter(
            mouse__group__pilot_id=pilot_id
        )
        if len(group_ids) != 0:
            tumor_volumes = tumor_volumes.filter(
                mouse__group_id__in=group_ids
            )

        serialized_data = {}
        group_map = {}
        # Initialize group totals and counts for calculating averages
        group_totals = defaultdict(lambda: defaultdict(float))
        group_counts = defaultdict(lambda: defaultdict(int))

        for tumor_volume in tumor_volumes:
            group_name = tumor_volume.mouse.group.name
            series_name = tumor_volume.identifier
            data_point = [tumor_volume.week, tumor_volume.volume]

            # Update group totals and counts
            group_totals[group_name][tumor_volume.week] += tumor_volume.volume
            group_counts[group_name][tumor_volume.week] += 1

            if group_name not in serialized_data:
                serialized_data[group_name] = {}
                group_map[group_name] = {"id": tumor_volume.mouse.group.pk}

            if series_name not in serialized_data[group_name]:
                serialized_data[group_name][series_name] = {
                    "data": [], "status": tumor_volume.mouse.status}

            serialized_data[group_name][series_name]['data'].append(data_point)

        # Convert the serialized_data dictionary into a list of dictionaries
        result = [{'group_name': name, **group_map[name], "data": [{"name": series_name, **series_data} for series_name, series_data in data.items()]}
                  for name, data in serialized_data.items()]

        # Add group totals and averages to the result
        for group_name, weekly_totals in group_totals.items():
            group_total_data = [[week, round(total_volume, 2)]
                                for week, total_volume in weekly_totals.items()]
            group_average_data = [[week, round(total_volume / group_counts[group_name][week], 2)]
                                  for week, total_volume in weekly_totals.items()]
            result_item = next(
                item for item in result if item['group_name'] == group_name)
            result_item['group_total'] = group_total_data
            result_item['group_average'] = group_average_data

        return JsonResponse({
            'data': result
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        pilotNumber = request.POST.get("pilot_id")
        file_raw = request.FILES['file']
        file = pd.ExcelFile(file_raw)
        for sheet in file.sheet_names:
            date_object = datetime.strptime(sheet, "%Y%m%d")
            date = date_object.timestamp() * 1000
            data = file.parse(sheet)
            columns = data.columns
            groupIndex = 0
            for index, row in data.iterrows():
                name = row[columns[1]]
                if (type(name) is str and 'mean' in name.lower()):
                    groupIndex += 1
                if (type(name) is not int or name > 10 or math.isnan(name)):
                    continue
                leftVol = row[columns[4]]
                rightVol = row[columns[7]]
                if (str(groupIndex) not in TUMOR_MAP[str(
                        pilotNumber)]):
                    continue
                identL = TUMOR_MAP[str(
                    pilotNumber)][str(groupIndex)] + str(name) + "L"
                identR = TUMOR_MAP[str(
                    pilotNumber)][str(groupIndex)] + str(name) + "R"
                mouse_id = mouse_id_map[identL]
                if (type(leftVol) is not str and math.isnan(leftVol) is False):
                    # TumorVolume()
                    TumorVolume.objects.update_or_create(
                        identifier=identL, week=date, defaults={"volume": round(leftVol, 2)}, mouse=mouse_id)
                if (type(rightVol) is not str and math.isnan(rightVol) is False):
                    # TumorVolume()
                    TumorVolume.objects.update_or_create(
                        identifier=identR, week=date, defaults={"volume": round(rightVol, 2)}, mouse=mouse_id)

        return JsonResponse({
            "message": "Success"
        })


# csrf_exempt


class Ivis(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        # Assuming pilot_id is passed as a query parameter
        pilot_id = request.GET.get('pilot_id')
        # Assuming group_ids is passed as a query parameter
        group_ids = request.GET.getlist('group_id[]')

        # Filter tumor volumes based on pilot_id and group_ids
        tumor_volumes = IvisData.objects.filter(
            mouse__group__pilot_id=pilot_id
        )
        if len(group_ids) != 0:
            tumor_volumes = tumor_volumes.filter(
                mouse__group_id__in=group_ids
            )

        serialized_data = {}
        group_map = {}
        # Initialize group totals and counts for calculating averages
        group_totals = defaultdict(lambda: defaultdict(float))
        group_counts = defaultdict(lambda: defaultdict(int))

        for tumor_volume in tumor_volumes:
            group_name = tumor_volume.mouse.group.name
            series_name = tumor_volume.identifier
            group_title = tumor_volume.mouse.group.title
            group_start = tumor_volume.mouse.group.started_at

            data_point = [tumor_volume.week, tumor_volume.value]

            # Update group totals and counts
            group_totals[group_name][tumor_volume.week] += tumor_volume.value
            group_counts[group_name][tumor_volume.week] += 1

            if group_name not in serialized_data:
                serialized_data[group_name] = {}
                group_map[group_name] = {
                    "id": tumor_volume.mouse.group.pk, "title": group_title, "started_at": group_start}

            if series_name not in serialized_data[group_name]:
                serialized_data[group_name][series_name] = {
                    "data": [], "status": tumor_volume.mouse.status, "reda": 43}

            serialized_data[group_name][series_name]['data'].append(data_point)

        # Convert the serialized_data dictionary into a list of dictionaries

        result = [{'group_name': name, **group_map[name], "data": [{"name": series_name, **series_data} for series_name, series_data in data.items()]}
                  for name, data in serialized_data.items()]

        # Add group totals and averages to the result
        for group_name, weekly_totals in group_totals.items():
            group_total_data = [[week, round(total_volume, 2)]
                                for week, total_volume in weekly_totals.items()]
            group_average_data = [[week, round(total_volume / group_counts[group_name][week], 2)]
                                  for week, total_volume in weekly_totals.items()]
            result_item = next(
                item for item in result if item['group_name'] == group_name)
            result_item['group_total'] = group_total_data
            result_item['group_average'] = group_average_data

        return JsonResponse({
            'data': result
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        file_raw = request.FILES['file']
        file = pd.ExcelFile(file_raw)

        first_sheet = file.sheet_names[0]
        df = file.parse(first_sheet)
        # Iterate over the DataFrame rows

        columns = df.columns

        daterow = None

        for index, row in df.iterrows():
            if (index == 0):
                daterow = row
            if (index < 1):
                continue
            name = row[columns[1]]
            if (type(name) is not str):
                continue
            for column in df.columns[2:]:
                date = pd.to_datetime(daterow[column],  format='%m/%d/%Y')
                date = int(date.timestamp()) * 1000
                value = row[column]
                if ((type(value) is not int and type(value) is not float) or math.isnan(value)):
                    continue
                print(f"I AM HERE")
                mouse_id = mouse_id_map[name]
                IvisData.objects.update_or_create(
                    identifier=name, week=date, defaults={"value": round(value, 2)}, mouse=mouse_id)
        return JsonResponse({
            "message": "Success"
        })


class PilotView(View):
    def get(self, request, *args, **kwargs):
        pilots = Pilot.objects.all()
        return JsonResponse({
            "data": list(pilots.values())
        })


class GroupView(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        pilot_id = request.GET['pilot_id']
        groups = Group.objects.filter(pilot_id=pilot_id).values()
        return JsonResponse({
            "data": list(groups)
        })


class Combined(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        pilot_id = request.GET.get('pilot_id')
        data = (
            IvisData.objects.filter(mouse__group__pilot_id=pilot_id)
            .annotate(identifier_week=Concat('identifier', Value('-'), 'week', output_field=CharField()))
            .values('identifier_week', 'value', 'mouse__tumorvolume__volume')
        )

        # Organizing the data into the desired format
        result = {}
        for entry in data:
            identifier_week = entry['identifier_week']
            ivis_value = entry['value']
            tumor_volume = entry['mouse__tumorvolume__volume']
            if identifier_week not in result:
                result[identifier_week] = {'name': identifier_week, 'data': []}
            result[identifier_week]['data'].append([ivis_value, tumor_volume])

        # Converting the dictionary into a list
        result_list = list(result.values())

        # Printing the result
        return JsonResponse({"data": result_list})


class Mice(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        group_id = request.GET.get("group_id")
        miceList = Mouse.objects.filter(group_id=group_id)
        return JsonResponse({
            "data": list(miceList.values())
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        mice = json.loads(request.body)['mouse_data']
        print(f"MICE ARE {mice}")
        for mouse in mice:
            Mouse.objects.filter(pk=mouse['id']).update(
                status=mouse['status'], updated_at=mouse['updated_at'], treatment_start=mouse['treatment_start'], first_screening=mouse['first_screening'])

        return JsonResponse({"status": "success"})


class Update(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        payload = json.loads(request.body)
        type = payload['type']
        data = payload['data']
        if (type == 'ivis'):
            for item in data:
                id = mouse_id_map[item['name']]
                IvisData.objects.update_or_create(
                    identifier=item['name'], week=item['date'], defaults={"value": round(item['value'], 2)}, mouse=id)
        else:
            for item in data:
                id = mouse_id_map[item['name']]
                TumorVolume.objects.update_or_create(
                    identifier=item['name'], week=item['date'], defaults={"volume": round(item['value'], 2)}, mouse=id)

        return JsonResponse({"status": "success"})
