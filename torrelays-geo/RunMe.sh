proxychains wget --dns-timeout=0 -p -k -e robots=off -H --span-hosts -U 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0' $1 -o $2
printf "$1" >> TestResults
printf " " >> TestResults
grep -n Downloaded $2 | tr -d '\n' >> TestResults
printf " " >> TestResults
grep -n "Total wall clock time" $2 | tr -d '\n' >> TestResults
printf " Distance: $3 " >> TestResults
printf "Scheme: $4 \n" >> TestResults
rm $2

array=($(echo */))

for i in "${array[@]}"
do
	rm -rf $i
done