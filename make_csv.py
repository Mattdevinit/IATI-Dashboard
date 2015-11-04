# Script to generate CSV files from data in the 'stats-calculated' folder, and extra logic in other files in this repository

import unicodecsv
import os
import data
from collections import OrderedDict

publisher_name={publisher:publisher_json['result']['title'] for publisher,publisher_json in data.ckan_publishers.items()}

def publisher_dicts():
    for publisher, activities in data.current_stats['inverted_publisher']['activities'].items():
        publisher_stats = data.get_publisher_stats(publisher) 
        yield {
            'Publisher Name': publisher_name[publisher],
            'Publisher Registry Id': publisher,
            'Activities': activities,
            'Organisations': publisher_stats['organisations'],
            'Files': publisher_stats['activity_files']+publisher_stats['organisation_files'],
            'Activity Files': publisher_stats['activity_files'],
            'Organisation Files': publisher_stats['organisation_files'],
            'Total File Size': publisher_stats['file_size'],
            'Reporting Org on Registry': data.ckan_publishers[publisher]['result']['publisher_iati_id'],
            'Reporting Orgs in Data (count)': len(publisher_stats['reporting_orgs']),
            'Reporting Orgs in Data': ';'.join(publisher_stats['reporting_orgs']),
            'Data Tickets': len(data.data_tickets[publisher]),
            'Hierarchies (count)': len(publisher_stats['hierarchies']),
            'Hierarchies': ';'.join(publisher_stats['hierarchies']),
        }

with open(os.path.join('out', 'publishers.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, [
        'Publisher Name',
        'Publisher Registry Id',
        'Activities',
        'Organisations',
        'Files',
        'Activity Files',
        'Organisation Files',
        'Total File Size',
        'Reporting Org on Registry',
        'Reporting Orgs in Data (count)',
        'Reporting Orgs in Data',
        'Data Tickets',
        'Hierarchies (count)',
        'Hierarchies',
        ])
    writer.writeheader()
    for d in publisher_dicts():
        writer.writerow(d)



publishers = data.current_stats['inverted_publisher']['activities'].keys()

with open(os.path.join('out', 'elements.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, [ 'Element' ] + publishers )
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

with open(os.path.join('out', 'elements_total.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, [ 'Element' ] + publishers )
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements_total'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

with open(os.path.join('out', 'registry.csv'), 'w') as fp:
    keys = ['name', 'title', 'publisher_frequency', 'publisher_frequency_select', 'publisher_implementation_schedule', 'publisher_ui', 'publisher_field_exclusions', 'publisher_contact', 'image_url', 'display_name', 'publisher_iati_id', 'publisher_units', 'publisher_record_exclusions', 'publisher_data_quality', 'publisher_country', 'publisher_description',  'publisher_refs', 'publisher_thresholds' 'publisher_agencies', 'publisher_constraints', 'publisher_organization_type', 'publisher_segmentation', 'license_id', 'state', 'publisher_timeliness']
    writer = unicodecsv.DictWriter(fp, keys)
    writer.writeheader()
    for publisher_json in data.ckan_publishers.values():
        writer.writerow({x:publisher_json['result'].get(x) or 0 for x in keys})



# Timeliness CSV files (frequency and timelag)
import timeliness
previous_months = timeliness.previous_months_reversed

for fname, f, assessment_label in (
    ('timeliness_frequency.csv', timeliness.publisher_frequency_sorted, 'Frequency'),
    ('timeliness_timelag.csv', timeliness.publisher_timelag_sorted, 'Time lag')
    ):
    with open(os.path.join('out', fname), 'w') as fp:
        writer = unicodecsv.writer(fp)
        writer.writerow(['Publisher Name', 'Publisher Registry Id'] + previous_months + [assessment_label])
        for publisher_title, publisher, per_month,assessment in f():
            writer.writerow([publisher_title, publisher] + [per_month.get(x) or 0 for x in previous_months] + [assessment])



# Transaction CSV file (transactions by type and year for all publishers)
with open(os.path.join('out', 'transactions_type_year.csv'), 'w') as fp:
    writer = unicodecsv.writer(fp)
    # Write column headers
    writer.writerow(['Publisher Name', 'Publisher Registry Id', 'Transaction type', 'Currency', 'Transaction year', 'Value'])
    
    # Get the aggregated publisher data
    agg_publisher_data = data.JSONDir('./stats-calculated/current/aggregated-publisher')

    # Loop over publishers
    for publisher_list in data.publishers_ordered_by_title:
        publisher_title = publisher_list[0]
        publisher_reg_id = publisher_list[1]
        
        # Loop over each expenditure type in sum_transactions_by_type_by_year
        for exp_type in agg_publisher_data[publisher_reg_id]['sum_transactions_by_type_by_year']:
            
            # Loop over each currency 
                for currency in agg_publisher_data[publisher_reg_id]['sum_transactions_by_type_by_year'][exp_type]:

                    # Loop over each year
                        for year in agg_publisher_data[publisher_reg_id]['sum_transactions_by_type_by_year'][exp_type][currency]:
                            
                            # Write the value for each year
                            value = agg_publisher_data[publisher_reg_id]['sum_transactions_by_type_by_year'][exp_type][currency][year]
                            writer.writerow([publisher_title, publisher_reg_id, exp_type, currency, year, value])


# Number of activities per publisher
with open(os.path.join('out', 'activities_per_publisher.csv'), 'w') as fp:
    writer = unicodecsv.writer(fp)
    # Write column headers
    writer.writerow(['Publisher Name', 'Publisher Registry Id', 'Number of activities'])
    
    # Get the aggregated publisher data
    agg_publisher_data = data.JSONDir('./stats-calculated/current/aggregated-publisher')

    # Loop over publishers
    for publisher_list in data.publishers_ordered_by_title:
        publisher_title = publisher_list[0]
        publisher_reg_id = publisher_list[1]
        
        # Write the value for each year
        writer.writerow([publisher_title, publisher_reg_id, agg_publisher_data[publisher_reg_id]['activities']])


# Forward-looking CSV file
import forwardlooking

with open(os.path.join('out', 'forwardlooking.csv'), 'w') as fp:
    writer = unicodecsv.writer(fp)
    writer.writerow(['Publisher Name', 'Publisher Registry Id'] + [ '{} ({})'.format(header, year) for header in forwardlooking.column_headers for year in forwardlooking.years])
    for row in forwardlooking.table():
        writer.writerow([row['publisher_title'], row['publisher']] + [ year_column[year] for year_column in row['year_columns'] for year in forwardlooking.years])



# Comprehensiveness CSV files ('summary', 'core', 'financials' and 'valueadded')
import comprehensiveness

for tab in comprehensiveness.columns.keys():
    with open(os.path.join('out', 'comprehensiveness_{}.csv'.format(tab)), 'w') as fp:
        writer = unicodecsv.writer(fp)
        writer.writerow(['Publisher Name', 'Publisher Registry Id'] +
                [ x+' (valid)' for x in comprehensiveness.column_headers[tab] ] +
                [ x+' (all)' for x in comprehensiveness.column_headers[tab] ])
        for row in comprehensiveness.table():
            writer.writerow([row['publisher_title'], row['publisher']]
                    + [ row[slug+'_valid'] if slug in row else '-' for slug in comprehensiveness.column_slugs[tab] ]
                    + [ row[slug] if slug in row else '-' for slug in comprehensiveness.column_slugs[tab] ])

