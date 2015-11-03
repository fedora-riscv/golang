#! /bin/bash
tar -xzf $1
cat ./go/src/compress/testdata/Mark.Twain-Tom.Sawyer.txt |tail -n +25 | head -n 8465 > ./go/src/compress/testdata/Mark.Twain-Tom.Sawyer.txt.new
mv ./go/src/compress/testdata/Mark.Twain-Tom.Sawyer.txt.new ./go/src/compress/testdata/Mark.Twain-Tom.Sawyer.txt
rm -f ./go/src/compress/bzip2/testdata/Mark.Twain-Tom.Sawyer.txt.bz2
rm $1
tar -czf $1 ./go
rm -rf ./go
