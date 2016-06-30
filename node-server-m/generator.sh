
# File sizes
fileSizes=(10000 100000 1000000 10000000 100000000 1000000000)

for i in "${fileSizes[@]}"
do
	echo $i
   	dd if=/dev/zero of=$i bs=$i count=1
done