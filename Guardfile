guard :shell do
    watch(/^(tests|gargoyle)(.*)\.py$/) do |match|
        puts `python setup.py nosetests`
    end
end