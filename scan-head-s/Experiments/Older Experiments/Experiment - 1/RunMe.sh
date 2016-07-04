proxychains wget -p -k -e robots=off -H --span-hosts -U 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0' $1 -o $2
printf "$1" >> TotalResults
printf " " >> TotalResults
grep -n Downloaded $2 | tr -d '\n' >> TotalResults
printf " " >> TotalResults
grep -n "Total wall clock time" $2 | tr -d '\n' >> TotalResults
printf " Distance: $3 " >> TotalResults
printf "Scheme: $4 \n" >> TotalResults
rm $2

array=($(echo */))

for i in "${array[@]}"
do
	rm -rf $i
done