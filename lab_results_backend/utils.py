from datetime import datetime, timedelta
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import Cast
from lab_results_backend_db.models import Pilot, Group, Mouse, TumorVolume, IvisData
from django.db.models import CharField


def convert_to_datetime(date_str) -> datetime:
    if date_str:
        return datetime.strptime(date_str, '%Y-%m-%d')
    return None


def study_duration(pilot_id):
    pilot = Pilot.objects.get(pk=pilot_id)
    start_date = convert_to_datetime(pilot.start_date)
    end_date = convert_to_datetime(pilot.end_date)
    return start_date, end_date


def percentage_sacrificed(pilot_id):
    total_mice = Mouse.objects.filter(group__pilot_id=pilot_id).count()
    sacrificed_mice = Mouse.objects.filter(
        group__pilot_id=pilot_id, status='sacrificed').count()
    return (sacrificed_mice / total_mice) * 100 if total_mice != 0 else 0


def average_days_to_sacrifice(pilot_id):
    pilot = Pilot.objects.get(pk=pilot_id)
    sacrificed_mice = Mouse.objects.filter(group__pilot_id=pilot_id, status='sacrificed').exclude(
        treatment_start__isnull=True, updated_at__isnull=True)
    if sacrificed_mice:
        total_days = 0
        total_days_from_start = 0
        for mouse in sacrificed_mice:
            treatment_start_date = convert_to_datetime(mouse.treatment_start)
            if treatment_start_date:
                sacrifice_date = convert_to_datetime(mouse.updated_at)
                if sacrifice_date:
                    if pilot.start_date:
                        total_days_from_start += (sacrifice_date -
                                                  convert_to_datetime(pilot.start_date)).days
                    total_days += (sacrifice_date - treatment_start_date).days
        return total_days / len(sacrificed_mice), total_days_from_start / len(sacrificed_mice)
    return 0, 0


def average_days_to_dead(pilot_id):
    pilot = Pilot.objects.get(pk=pilot_id)
    dead_mice = Mouse.objects.filter(group__pilot_id=pilot_id, status='dead').exclude(
        treatment_start__isnull=True, updated_at__isnull=True)
    if dead_mice:
        total_days = 0
        total_days_from_start = 0
        for mouse in dead_mice:
            treatment_start_date = convert_to_datetime(mouse.treatment_start)
            if treatment_start_date:
                death_date = convert_to_datetime(mouse.updated_at)
                if death_date:
                    if pilot.start_date:
                        total_days_from_start += (death_date -
                                                  convert_to_datetime(pilot.start_date)).days
                    total_days += (death_date - treatment_start_date).days

        return total_days / len(dead_mice), total_days_from_start / len(dead_mice)
    return 0, 0


def percentage_died(pilot_id):
    total_mice = Mouse.objects.filter(group__pilot_id=pilot_id).count()
    dead_mice = Mouse.objects.filter(
        group__pilot_id=pilot_id, status='dead').count()
    return (dead_mice / total_mice) * 100 if total_mice != 0 else 0


def average_tumor_growth(pilot_id, treatment_start_date):
    if treatment_start_date is None:
        return 0
    ivis_identifiers = IvisData.objects.filter(
        mouse__group__pilot_id=pilot_id).values_list('identifier', flat=True).distinct()

    total_tumor_growth = 0
    count = 0

    for identifier in ivis_identifiers:
        first_entry_before_treatment = IvisData.objects.filter(mouse__group__pilot_id=pilot_id, identifier=identifier).filter(
            mouse__treatment_start__lt=treatment_start_date).order_by('week').first()
        last_entry_before_treatment = IvisData.objects.filter(mouse__group__pilot_id=pilot_id, identifier=identifier).filter(
            mouse__treatment_start__lt=treatment_start_date).order_by('week').last()

        if first_entry_before_treatment and last_entry_before_treatment:
            first_value = float(first_entry_before_treatment.value)
            last_value = float(last_entry_before_treatment.value)
            tumor_growth = last_value - first_value
            total_tumor_growth += tumor_growth
            count += 1

    return total_tumor_growth / count if count != 0 else 0


def date_to_timestamp(date_str):
    if not date_str:
        return None
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    timestamp = int(date_obj.timestamp()) * 1000  # Convert to milliseconds
    return timestamp


def average_growth_after_treatment(pilot_id):
    # Get all mice
    mice = Mouse.objects.filter(group__pilot_id=pilot_id).all()

    growth_sum = 0
    growth_count = 0

    # Iterate over each mouse
    for mouse in mice:

        # Get the first entry after treatment start for the mouse
        treatment_start_ts = date_to_timestamp(mouse.treatment_start)
        if treatment_start_ts:
            first_entry_after_treatment_start = TumorVolume.objects.filter(
                mouse=mouse,
                week__gte=treatment_start_ts
            ).order_by('week').first()

            if first_entry_after_treatment_start:
                # Get the last entry for the mouse (assuming it's the last recorded entry)
                last_entry = TumorVolume.objects.filter(
                    mouse=mouse,
                    week__lt=treatment_start_ts
                ).order_by('-week').first()

                # Calculate growth if last entry exists
                if last_entry:
                    growth = last_entry.volume - first_entry_after_treatment_start.volume
                    growth_sum += growth
                    growth_count += 1

    # Calculate the average growth
    if growth_count > 0:
        average_growth = growth_sum / growth_count
        return average_growth
    else:
        return 0  # No data available or no mice with valid data


def calculate_metrics(pilot_id):
    average_data = calculate_average_tumor_growth_per_week(pilot_id)
    formatted_average_data = format_for_chartjs(average_data)
    pilot = Pilot.objects.get(pk=pilot_id)
    (from_treatment_start, from_study_start) = average_days_to_sacrifice(pilot_id)
    (dead_from_treatment_start, dead_from_study_start) = average_days_to_dead(pilot_id)
    start_date, end_date = study_duration(pilot_id)
    sacrificed_percentage = percentage_sacrificed(pilot_id)
    days_to_sacrifice = {
        "from_treatment_start": from_treatment_start, "from_study_start": from_study_start}
    days_to_dead = {
        "from_treatment_start": dead_from_treatment_start, "from_study_start": dead_from_study_start}
    average_tumor_growth_before = average_tumor_growth(
        pilot_id, pilot.start_date)
    average_growth_after = average_growth_after_treatment(
        pilot_id)
    # Additional calculations can be done for average days from start of treatment to event
    # and for plotting the line graph for tumor growth after treatment
    # These calculations depend on more specific requirements and data structures
    res = {
        'study_duration': {'start': start_date, 'end': end_date},
        'sacrificed_percentage': sacrificed_percentage,
        'average_days_to_sacrifice': days_to_sacrifice,
        'average_days_to_dead': days_to_dead,
        'percentage_died': percentage_died(pilot_id),
        'average_tumor_growth_before': average_tumor_growth_before,
        'average_growth_after': average_growth_after,
        'weekly_average_growth_after_treatment': formatted_average_data
    }

    return res


def calculate_average_tumor_growth_per_week(pilot_id):
    # Get distinct weeks and groups
    distinct_weeks = TumorVolume.objects.values_list(
        'week', flat=True).distinct()
    distinct_groups = Group.objects.filter(pilot_id=pilot_id).all()

    # Iterate over distinct weeks and groups
    result = {}
    for week in distinct_weeks:
        for group in distinct_groups:
            # Get tumor volumes for the group and week
            tumor_volumes = TumorVolume.objects.filter(
                mouse__group=group, week=week)

            # Calculate average tumor growth for the group and week
            # Considering only tumor volumes recorded after treatment_start of each mouse
            average_growth = tumor_volumes.filter(
                mouse__treatment_start__lte=week).aggregate(Avg('volume'))['volume__avg']

            # Store the result
            if average_growth:
                result.setdefault(week, {})[group.name] = average_growth

    return result


def format_for_chartjs(response):
    datasets = []
    group_names = set()

    # Collect all group names
    for week_data in response.values():
        group_names.update(week_data.keys())

    # Initialize datasets for each group
    for group_name in group_names:
        datasets.append({
            "name": group_name,
            "data": [],
        })

    # Fill in data for each group
    for week, week_data in response.items():
        for i, group_data in enumerate(datasets):
            group_name = group_data["name"]
            if group_name in week_data:
                group_data["data"].append(round(week_data[group_name], 2))
            else:
                group_data["data"].append(0)  # Append None for missing data

    return {
        # Convert week timestamps to strings
        "labels": [str(week) for week in response.keys()],
        "datasets": datasets
    }
