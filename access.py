#!/usr/local/bin/python3
import shopify
from datetime import datetime, timedelta
import timestring
import csv
import time
import json

"""API Key, Password and Shop Name removed""" 
CLIENT_SECRET_FILE = ''

API_KEY = 'SHOPIFY API KEY'
PASSWORD = 'SHOP PASSWORD HERE'
SHOP_NAME = 'SHOP NAME HERE'


def shopify_login():
	"""Logs into Shopify API"""
	shop_url = "https://%s:%s@%s.myshopify.com/admin" % (API_KEY, PASSWORD, SHOP_NAME)
	shopify.ShopifyResource.set_site(shop_url)
	shop = shopify.Shop.current()
	return shop

def get_order_list(page):
	"""Pulls list of orders by page from Shopify"""
	order_list = shopify.Order.find(status="any",page=page)
	return order_list

def string_to_date(date):
	"""Edits Date information pulled from Shopify 
	so date  can be turned into string 
	"""
	date = timestring.Date(date)
	date_string = str(date)
	date_string_split = date_string.split(' ')
	real_date = datetime.strptime(date_string_split[0], '%Y-%m-%d')
	return real_date


if __name__ == "__main__":
	shop = shopify_login()
	starttime = datetime.now()
	starttime_string = str(starttime)
	print(("This job started running at %s") % (starttime_string))
	page = 1
	deliverys_data = [] 
	while page < 3:
		order_list = get_order_list(page)
		for i in order_list:
			fulfillments = i.get("fulfillments")
			try:
				# Changing these to pull from initial fulfillment dictionary above changes logic
				# TODO: Fix logic so we don't have to use so many get requests
				destination_information = fulfillments[0].get('line_items')[0].get('destination_location')
				tracking_url = fulfillments[0].get('tracking_url')
				appx_closeddate = fulfillments[0].get('updated_at')
				created_date = fulfillments[0].get('created_at')
				# Calculates time difference between order creation and date order closed
				# Order close date is an approximation of delivery date
				real_appx_closeddate = string_to_date(appx_closeddate)
				real_created_date = string_to_date(created_date)
				time_difference = real_appx_closeddate - real_created_date
				try:
					customer_name = destination_information.get('name')
					shipment_status = fulfillments[0].get("shipment_status")
					deliverys_data.append([customer_name, shipment_status, time_difference])
					print("Customer Name: %s\nShipment Status:%s\nTime To Deliver: %s\n\n" %(customer_name,shipment_status, time_difference))
				except AttributeError:
					deliverys_data.append(["N/A", "Delivered", "Order Manually Created"])
					print("No Information: Manually Created Order\n\n")
			except IndexError:
				print("Unfulfilled") 
			time.sleep(1)
		page += 1

	with open('shopify_new_data.csv', 'w') as csvfile:
		out = csv.writer(csvfile)
		headers = ["Customer Name", "Shipment Status", "Time to Deliver"]
		out.writerow(headers)
		for delivery_data in deliverys_data:
			out.writerow(delivery_data)
				
	endtime = datetime.now() - starttime
	endtime_string = str(endtime)
	print(("This job stopped running after %s") % (endtime_string))
