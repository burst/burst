all:
	javac src/*.java
	cd src && jar cmf mainClass GameController.jar *.class && cd ..
	mv src/GameController.jar .

clean:
	rm -fr src/*.class
	rm -fr *.jar
