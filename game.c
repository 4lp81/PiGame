#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>
#include <curl/curl.h>
#include <string.h>

#define PIR_PIN 23

size_t write_callback(void *ptr, size_t size, size_t nmemb, void *stream) {
    // Schreibe die Antwort direkt auf die Konsole
    fwrite(ptr, size, nmemb, stdout);
    return size * nmemb;
}

void send_solution(const char* puzzleId, const char* givenSolution) {
    CURL *curl;
    CURLcode res;
    struct curl_slist *headers = NULL;

    char data[256];
    snprintf(data, sizeof(data), "{\"puzzleId\":\"%s\", \"givenSolution\":\"%s\"}", puzzleId, givenSolution);

    // Ausgabe JSON-Request
    printf("Sending Request: %s\n", data);

    curl = curl_easy_init();
    if(curl) {
        headers = curl_slist_append(headers, "Content-Type: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/solution");
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);

        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    } else {
        fprintf(stderr, "Fehler bei der Initialisierung von libcurl.\n");
    }
}


int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "Fehler beim Initialisieren von pigpio.\n");
        return 1;
    }

    if (gpioSetMode(PIR_PIN, PI_INPUT) != 0) {
        fprintf(stderr, "Fehler beim Setzen des GPIO-Modus.\n");
        gpioTerminate();
        return 1;
    }

    if (gpioSetPullUpDown(PIR_PIN, PI_PUD_DOWN) != 0) {
        fprintf(stderr, "Fehler beim Setzen des Pull-Down-Widerstands.\n");
        gpioTerminate();
        return 1;
    }

    printf("Bewegungssensor-Test\n");

    int sensorState = 0;

    while (1) {
        int currentState = gpioRead(PIR_PIN);

        if (currentState == 1 && sensorState == 0) {
            printf("Bewegung erkannt!\n");
            send_solution("6560a4e9414e841c83929236", "1"); // puzzleId und givenSolution anpassen
            sensorState = 1;
        } else if (currentState == 0 && sensorState == 1) {
            printf("Keine Bewegung.\n");
            sensorState = 0;
        }

        usleep(100000); // Verzögerung von 100 Millisekunden
    }

    gpioTerminate(); // Am Ende des Programms aufrufen

    return 0;
}
