proxychains wget $1 -o $2

# proxychains curl -k -o TEMP_FILE 'https://203.135.63.12:16667/$1' 2>&1 | tee $2
# rm TEMP_FILE


printf "Result: $1" >> TotalResults
printf " " >> TotalResults
grep -n 100% $2 | tr -d '\n' >> TotalResults
printf " " >> TotalResults
printf " $3 " >> TotalResults
printf " $4 " >> TotalResults
printf " $5 " >> TotalResults
printf " $6 " >> TotalResults
printf " $7 " >> TotalResults
printf " $8 " >> TotalResults
printf " $9 " >> TotalResults
printf " ${10} " >> TotalResults
printf " ${11}\n" >> TotalResults
rm $2

# array=($(echo */))

# for i in "${array[@]}"
# do
# 	rm -rf $i
# done
