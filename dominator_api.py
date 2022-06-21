import csv
import os
import glob
from prettytable import PrettyTable
from operator import itemgetter
import time

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

#Function to load baseline from file taken from input and store in a dict
def load_baseline():
	baseline = {}
	global baseline_path
	baseline_path = input("Enter the baseline file path: ")
	# baseline_path = '/Users/rchinmay/Documents/baseline.csv'
	# baseline_path = '/Users/rchinmay/Documents/Custom_Query/pages/Query_Command2.csv'
	with open(baseline_path) as f:
		csvr = csv.reader(f)
		header = next(csvr)
		global count
		count = int(next(csvr)[0])
		for row in csvr:
			baseline[row[0]] = row[1:5]
	return baseline

#Function to update baseline as average for each entry
def add_data_to_baseline(data, baseline):
	global count
	global baseline_path
	hash_val = {ele[0]:ele[1:] for ele in data}
	for val in data:
		if val[0] not in baseline:
			baseline[val[0]]=[0,0,0,0.0]
	for key,value in baseline.items():
		value = list(map(float, value))
		for i in range(4):
			value[i]*=count
			value[i]+=float(hash_val.get(key, [0,0,0,0])[i])
			value[i]/=(1+count)
		baseline[key] = value
	count += 1
	print('baseline')
	# print(baseline)
	sorted_total = sorted(baseline.items(), key = lambda x: x[1][3], reverse = True)
	with open(baseline_path, 'w') as f:
		csvr = csv.writer(f)
		csvr.writerow(['Class Name','Objects', 'Shallow Heap', 'Retained Heap', 'Percentage of Retained Heap'])
		csvr.writerow([count])
		# csvr.writerows(sorted_total)
		for row in sorted_total:
			lis = [row[0], int(row[1][0]), int(row[1][1]), int(row[1][2]), round(float(row[1][3]), 3)]
			csvr.writerow(lis)

#FORMAT OF DOMINATOR CSV OUTPUT:
#Class Name,Objects,Shallow Heap,Retained Heap,Percentage,

if __name__ == '__main__':
	t = time.process_time()
	t1 = time.time()
	heap_filename = input("Enter the absolute path to heap_dump: ")
	heap_filename.strip()
	# heap_filename = '/Users/rchinmay/Documents/java_pid48008.hprof'
	# heap_filename = '/Users/rchinmay/Desktop/Parser/biggestHeap.hprof'
	if(heap_filename[-6:] != '.hprof'):
		print('You enterred: ' + heap_filename + '. Last characters are: ' + heap_filename[-6:])
		print('Heap File name should end in ".hprof"')
		os._exit(-1)
	print('Running dominator_tree command using MAT api.')
	os.system('/Applications/mat.app/Contents/Eclipse/ParseHeapDump.sh '+heap_filename+' -command="dominator_tree -groupBy BY_CLASS" -format=csv -unzip org.eclipse.mat.api:query')
	csv_folder = heap_filename[:-6] + '_Query/pages'
	filenames = glob.glob(csv_folder + '/*.csv')
	all_data = []
	for file in filenames:
		with open(file, 'r') as f:
			csvr = csv.reader(f)
			header = next(csvr)
			for row in csvr:
				row[4]=float(row[4])*100
				all_data.append(row)
	print("\nLength: ", len(all_data))
	baseline = {}
	baseline = load_baseline()
	# Print tablular output
	table = PrettyTable(['ClassName', 'Objects', 'Objects(S-B)', 'Shallow Heap', 'Shallow Heap(S-B)', 'Retained Heap', 'Retained Heap(S-B)', 'Percentage', 'Percentage(S-B)'])
	# Number of rows to print in compared dominator classes
	num_rows = 50
	for row in all_data:
		className,objects,shallow_heap,retained_heap,percentage = row[:5]
		objects = int(objects)
		shallow_heap = int(shallow_heap)
		retained_heap = int(retained_heap)
		baseline_row = list(map(float, baseline.get(className, [0,0,0,0.0])))
		new_row = [className, objects, int(objects - baseline_row[0]), shallow_heap, int(shallow_heap - baseline_row[1]), retained_heap, int(retained_heap - baseline_row[2]), round(percentage, 3), round(percentage - baseline_row[3], 3)]
		table.add_row(new_row)
	print("-"*100)
	print("DOMINATOR TREE COMPARISON TABLE: ")
	print(table.get_string(start=0, end=num_rows, sort_key=itemgetter(8,9), sortby='Percentage', reversesort=True))
	print('-'*100)
	print()
	#compare top n classes
	n = int(input("Enter the number of top classes to compare: "))
	for i in range(min(n, len(all_data))):
		temp_list = [ordinal(i+1), " dominator class is: ", '{'+', '.join(str(v) for v in all_data[i]) + '}', ", and its usage in basline is: ", '{'+', '.join(str(v) for v in baseline.get(all_data[i][0], (0,0,0,0)))+'}']
		print(''.join(temp_list))
	#Add data to baseline
	add_data_to_baseline(all_data, baseline)
	print('*'*100)
	print('*'*100)
	print('Elapsed CPU time: ', time.process_time() - t)
	print('Elapsed total time: ', time.time() - t1)
