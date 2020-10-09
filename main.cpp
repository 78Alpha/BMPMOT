#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <cmath>
#include <cstring>
#include <vector>
#include <variant>


const unsigned char constHeader[] = "\x42\x4d\xd2\xe4\xde\x02\x00\x00\x00\x00\x7a\x00\x00\x00\x6c\x00\x00\x00\x37\x13\x00\x00\xbf\x0c\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x58\xe4\xde\x02\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42\x47\x52\x73\x00\x00\x00\x00\x00\x00";
const char* stdOutput = "./Output";
uintmax_t chunkSize = 48000000;

void internalLogger(const std::string& logMessage){
    std::cout << "LOG | " << logMessage << std::endl;
}

void directoryCreation(const char* targetDir){
    try {
        std::filesystem::create_directory(targetDir);
    } catch (int exceptionInt) {
        std::cout << "Directory Exists: " << targetDir << " " << exceptionInt << std::endl;
    }
}

int deleteItem(const char *target){
    if( remove( target ) != 0 )
        return 1;
    return 0;
}

std::string createBmp(char *chunkData, int iteration, const std::string& name){
    internalLogger("Creating BMP...");

    std::ostringstream bitmapDirName;
    bitmapDirName << name << "." << iteration << ".bmp";

    const std::string targetToTargetDirectory = std::string(bitmapDirName.str());

    const char* bitmapNameConcrete = targetToTargetDirectory.c_str();
    std::cout << "Working With File " << bitmapNameConcrete << std::endl;
    internalLogger("Deleting Duplicate Files...");
    deleteItem(bitmapNameConcrete);
    std::ofstream outputBitmap;
    outputBitmap.open(bitmapNameConcrete, std::ios_base::app|std::ios_base::binary);
    if (outputBitmap.is_open()){
        internalLogger("File Open, Data Output Ready!");
    } else {
        internalLogger("Fatal Error, Output Not Open!");
        exit(1);
    }
    internalLogger("Attaching Header...");
    outputBitmap.write(reinterpret_cast<const char*>(constHeader), 64);
    internalLogger("Pushing Data...");
    outputBitmap.write(chunkData, chunkSize);
    internalLogger("Data Pushed! File Closed!");
    outputBitmap.close();
    return "string";
}

void chunk(uintmax_t fileSize, const std::string& rawName){
    internalLogger("Initiating Chunk...");
    internalLogger("Getting Iterable Chunks...");
    int iterableChunks= 0;
    double tempChunkState = 0;
    uintmax_t remainderSize = 0;
    bool useFileSize = false;

    if (chunkSize > fileSize){
        iterableChunks = 1;
        useFileSize = true;
        chunkSize = fileSize;
    } else {
        iterableChunks = round(fileSize / chunkSize);
        tempChunkState = remainder(fileSize, chunkSize);
        if (tempChunkState != 0){
            remainderSize = fileSize - (iterableChunks * chunkSize);
            iterableChunks += 1;
        }
    }

    std::ifstream inputFile;
    std::ostringstream rawDirNameStream;
    rawDirNameStream << stdOutput << "/" << rawName;
    std::string usableName = std::string(rawDirNameStream.str());

    const char* outputDirecotryName = usableName.c_str();

    char *chunkData = new char[chunkSize];
    internalLogger("Reading Data...");
    std::string name;
    int position = 0;

    inputFile.open(rawName, std::ios_base::in|std::ios_base::binary);
    if (inputFile.is_open()){
        internalLogger("File Open, Data Available");
    } else {
        internalLogger("File Not Open!");
        exit(0);
    }
    std::cout << "Operating on " << usableName << std::endl;
    if (useFileSize){
        internalLogger("Using File Size...");
        inputFile.read(chunkData, fileSize);
        internalLogger("Creating File...");
//        std::cout << "DATA | " << chunkData << std::endl;
        createBmp(chunkData, 0, outputDirecotryName);
        internalLogger("File Created!");
    } else {
        while (inputFile) {
            internalLogger("Using Chunks...");
            if (position == (iterableChunks - 1)) {
                inputFile.read(chunkData, fileSize);
                inputFile.close();
                internalLogger("Creating File...");
                createBmp(chunkData, position, outputDirecotryName);
                internalLogger("File Created! Adjusting Position...");
                position += 1;
            } else {
                internalLogger("Creating File...");
                inputFile.read(chunkData, remainderSize);
                createBmp(chunkData, position, outputDirecotryName);
                internalLogger("File Created! Adjusting Position...");
                position += 1;
            }
        }
    }
    delete [] chunkData;
}

void makeMaster(const std::string& inputFile){
    directoryCreation(stdOutput);
    std::uintmax_t fileSize;
    const std::filesystem::path filePath = std::filesystem::current_path() / inputFile;
    fileSize = std::filesystem::file_size(filePath);
    std::cout << "File Size: " << fileSize << std::endl;
    internalLogger("File Size Retrieved!");
    chunk(fileSize, inputFile);
}

int main(int argc, char *argv[])
{
    std::cout << "Command-line argument count: " << argc << " \n";
    std::cout << "Arguments:\n";
    if (argv[1] != nullptr){
        std::string fileName(argv[1]);
        fileName.erase(fileName.begin(), fileName.begin()+2);
        internalLogger(fileName);
        makeMaster(fileName);
    } else {
        internalLogger("No Argument Given!");
    }
    return 0;
}
