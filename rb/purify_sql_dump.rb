#/usr/bin/ruby
# coding: utf-8

# sql 공백을 제거해주는 ruby 파일

$PROGRAM_NAME = "purify_sql_dump"



if ARGV.length < 2
	puts "Usage:  #{$PROGRAM_NAME}  <input> <output>"
	exit			
end

# input
input = ARGV[0]
# output
output = ARGV[1]

if input.empty?
	puts "<input> have to exist"
	exit
end

if output.empty? 
	puts "<output have to exists"
	exit
end

File.open input.to_s, mode ='r'  do |inputFile|
	File.open output.to_s, mode = 'w' do |outputFile|
	
		commentSkip = false
		strArr = Array.new
		loop do
			begin 
				currentLine = inputFile.readline 
				if currentLine.strip.empty? 
					next
				end
				if currentLine.lstrip.start_with?('--') || currentLine.lstrip.start_with?('#')
					next
				end
				if currentLine.lstrip.start_with?('/*') 
					commentSkip = true
					next
				end
				if commentSkip && currentLine.index('*/') != nil 
					index = currentLine.index('*/') 
					currentLine = currentLine.slice index
				end
			
 				index = currentLine.strip.index ';'
				if index.nil?
					index = currentLine.strip.index '--'
				end
				if index.nil?
					strArr.push currentLine.strip	
					next
				elsif strArr.length != 0 
					currentLine = strArr.join('\n') + ";"
					strArr.clear
				else
					currentLine = currentLine.strip.slice 0, index
					currentLine += ";"
				end
			
				if currentLine.upcase.start_with?("INSERT") || currentLine.upcase.start_with?("UPDATE")
					outputFile.write currentLine
				end
				
			rescue Exception =>e
				puts e.message
				break
			end
		end
	end
end


