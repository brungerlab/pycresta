#!/bin/bash
##This script will read a .coords file and parse it by contour number and and line in contour.  For a given contour, the first point should be the vesicle interface while the second point should be the vesicle membrane, the third the approx vesicle center and the fourth to nth points should be vATPases.  

##TO USE: ./Coordsort.sh XXX.coords XXX

dir="$1" ##The original coords file
#OUT="$2" ##Whatever XXX.coordsI/M/C/V you want it to be named 
invert="$2"

if [[ -z "$invert" ]]
then
	echo proceeding without inverting Z coordinates...
else 
	echo will invert Z coordinates...
fi

for f in "$dir"/*/*.coords
do
awk < "$f" '{print $1}' | uniq > "tulist" 
j="$(basename "$f" .coords)"
##Reads the .coords file and counts how many unique contours you have then puts these into a temp file called "tuliset"

Iter=$( awk 'END {print NR}' tulist)


if [[ ! -z "$invert" ]]
then
	thickness=$(header $dir/$j/$j".rec" | grep Number | cut -f17 -d " ")
	awk '{ $3 = '$thickness' - $3; print }' $f > $f"invert"
	mv $f $f"orig"
	mv $f"invert" $f
fi

##for loop that will go through the number found in tulist.  This puts all of the contour number, x, y, and z into temp files for each coord type



for i in $(eval echo "{1..$Iter}")
do 
	awk '{ if($1 == '$i') { print > "cont'$i'" }}' "$f"
	
	cat cont"$i" | awk 'NR==1' >> testout_interface.coords
	cat cont"$i" | awk 'NR==2' >> testout_vmem.coords
	cat cont"$i" | awk 'NR==3' >> testout_vcent.coords
	cat cont"$i" | tail -n +4 >> testout_vATP.coords
	
	
rm cont"$i"


##This removes the contour number from the list and writes out the .coordsX files
cat testout_interface.coords | awk '{$1=""}1' >> "$dir"/"$j"/"$j".coordsI
cat testout_vmem.coords | awk '{$1=""}1' >> "$dir"/"$j"/"$j".coordsM
cat testout_vcent.coords | awk '{$1=""}1' >> "$dir"/"$j"/"$j".coordsC
cat testout_vATP.coords | awk '{$1=""}1' >> "$dir"/"$j"/"$j".coordsV


rm testout*
echo "done "$j""

done

done

rm tulist

