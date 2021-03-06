#!/usr/bin/env python3
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
"""
This module contains some utility functions
"""

# standard library
import os
import sys
import csv
import string
import random
import json
from collections import OrderedDict, defaultdict


def extract_info_from_csvfilename(csv_name):
    """
    extract maker, model, new/used info from csv_name

    Args:
        csv_name: csv filename

    Returns:
        car_info: a dictionary which contains maker/model/condition
    """
    if '/' in csv_name:
        csv_name = csv_name[csv_name.rfind('/') + 1: csv_name.rfind('.')]
    maker, model, *_, condition = csv_name.split('-')
    res = [maker, model, condition]
    car_info = dict(zip(('maker', 'model', 'condition'),
                        (item.upper() for item in res)))
    return car_info


def user_input():
    """
    parse command line args

    Returns:
        A tuple contains search query
    """
    if len(sys.argv) != 8:
        print(
            "Usage: >> python {} <maker> <model> <zip> <radius> <used or new> <json or keyfile> <output_dir>".format(
                sys.argv[0]))
        print(
            "e.g. python {} Honda Accord 53715 25 used <json or keyfile> ./data/".format(sys.argv[0]))
        sys.exit(1)
    # need to add validation check
    maker = sys.argv[1]
    model = sys.argv[2]
    zipcode = int(sys.argv[3])
    radius = int(sys.argv[4])
    condition = sys.argv[5]
    extra_file = sys.argv[6]
    output_dir = sys.argv[7]
    # if the output_dir does not exist, create it
    os.makedirs(output_dir, exist_ok=True)
    return (maker, model, zipcode, radius, condition, extra_file, output_dir)


def write_cars_to_csv(csv_name, csv_header, csv_rows):
    """
    create csv file and write rows to the csv file

    Args:
        csv_name: csv filename
        csv_header: csv header name
        csv_rows: csv rows
    """
    # delete previous csv file with the same name
    if os.path.exists(csv_name):
        try:
            os.remove(csv_name)
            print("delete previous {}".format(csv_name))
        except OSError:
            print("error in deleting {}".format(csv_name))
            sys.exit(1)
    with open(csv_name, 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=csv_header)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
    print(
        "Writing {:d} cars information to {:s}".format(
            len(csv_rows),
            csv_name))


def guess_car_brand(data_file='model_codes_carscom.csv'):
    """
    A terminal game which lets user guess car brand

    Args:
        data_file: model codes for cars.com
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_file = os.path.join(dir_path, 'model_codes_carscom.csv')
    if not os.path.exists(data_file):
        extract_maker_model_codes(data_file)
    num_questions = 10
    num_correct = 0
    num_choices = 4
    letters = string.ascii_uppercase[:num_choices]
    # load data, prepare brands and model_brand_pairs
    brands = set()
    model_brand_pairs = {}
    with open(data_file, 'r') as f:
        reader = csv.DictReader(f)
        for line in reader:
            brands.add(line['maker'])
            model_brand_pairs[line['model']] = line['maker']
    # question loop
    count = num_questions
    question_num = 0
    while count > 0:
        count -= 1
        model, brand = random.choice(list(model_brand_pairs.items()))
        question_num += 1
        print("{:d}. What is the brand of {}? (choose one from {} to {})".
              format(question_num, model, letters[0], letters[-1]))
        choices = random.sample(brands, num_choices - 1)
        choices.append(brand)
        random.shuffle(choices)
        d = OrderedDict(zip(letters, choices))
        for letter, choice in d.items():
            print("{}. {}  ".format(letter, choice), end="")
        print()
        # wait until user pick a valid choice
        while True:
            user_choice = input("> ")
            user_choice = user_choice.upper()
            if user_choice in letters:
                break
            else:
                print("please pick a valid choice")
        if user_choice in d and d[user_choice] == brand:
            print("correct!")
            num_correct += 1
        else:
            print("wrong!")
            print("{} belongs to {}!".format(model, brand))
    print("Score {:d}/{:d}".format(num_correct, num_questions))


def extract_maker_model_codes(csv_name):
    """
    open cars_com_make_model.json file, read it, and
    extract maker and model cars.com code and store in a csv file

    Args:
        csv_file: csv filename
    """
    csv_header = ['maker', 'model', 'maker code', 'model code']
    csv_rows = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data = json.load(open(os.path.join(dir_path, 'cars_com_make_model.json')))
    data = data['all']
    car_dict = {}
    for i, maker in enumerate(data, 1):
        car_dict['maker'] = maker['nm'].strip()  # name
        car_dict['maker code'] = maker['id']    # id
        for j, model in enumerate(maker['md'], 1):
            model_name = model['nm'].strip()
            if model_name[0] == '-':
                model_name = model_name[1:].strip()
            car_dict['model'] = model_name
            car_dict['model code'] = model['id']
            csv_rows.append(dict(car_dict))
    write_cars_to_csv(csv_name, csv_header, csv_rows)


if __name__ == "__main__":
    print("Welcome to automotive brand guessing game!")
    guess_car_brand()
