from collections import namedtuple
import csv

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from djaveTable.cell_content import StringContent, InHref


def csv_writer_and_response(file_name='unhelpful_generic_file_name.csv'):
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = (
      'attachment; filename="{}"'.format(file_name))
  writer = csv.writer(response)
  return writer, response


CanCSVResponse = namedtuple(
    'CanCSVResponse', 'template context table csv_file_name')


class CanCSV(object):
  """ Use this to decorate functions that usually return HTML, but when ?csv is
  in the query string, you want to return a CSV, probably of the table on the
  page.

  The view has to return a CanCSVResponse. """
  def __init__(self, view_function):
    self.view_function = view_function

  def __call__(self, request, *args, **kwargs):
    can_csv_response = self.view_function(request, *args, **kwargs)
    if not isinstance(can_csv_response, CanCSVResponse):
      raise Exception(
          'Views with the CanCSV decorator must return a CanCSVResponse')
    if 'csv' in request.GET:
      return table_to_csv_response(
          can_csv_response.table, can_csv_response.csv_file_name)
    else:
      can_csv_response.table.post_table_buttons.insert(
          0, download_csv_button())
      return render(
          request, can_csv_response.template, can_csv_response.context)


def download_csv_button():
  button = InHref(
      'Download CSV', '', classes=['download_csv_button'], button=True)
  return StringContent(
      render_to_string('download_csv_button.html', {'button': button}))


def table_to_csv_response(table, file_name):
  writer, response = csv_writer_and_response(file_name)
  table.write_csv(writer)
  return response
