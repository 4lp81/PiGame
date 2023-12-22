#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>


int main() {
    // Specify the URL of the game on the server
    const char* gameUrl = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/downloads/puzzles/helloworld";

    // Specify the local path to save the downloaded game
    const char* localPath = "/home/pi17/helloworld.exe";

    // Use wget to download the game
    char wgetCommand[256];
    snprintf(wgetCommand, sizeof(wgetCommand), "wget -O %s %s", localPath, gameUrl);
    int wgetResult = system(wgetCommand);

    if (wgetResult == 0) {
        printf("Game downloaded successfully.\n");

        // Make the downloaded file executable
        chmod(localPath, 0777);

        // Execute the downloaded game
        int execResult = execl(localPath, "game.exe", NULL);

        if (execResult == -1) {
            perror("Error executing the game");
            return EXIT_FAILURE;
        }
    } else {
        fprintf(stderr, "Error downloading the game.\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
