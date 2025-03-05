#ifndef HTTP_CLIENT_H
#define HTTP_CLIENT_H

#include <iostream>
#include <string>
#include <vector>
#include <curl/curl.h>
#include <memory>
#include <mutex>
#include <future>
#include <thread>
#include <optional>

class HTTPClient {
public:
    static std::string sendGETRequest(const std::string& url, const std::vector<std::string>& headers = {}) {
        return sendRequest(url, headers, std::nullopt);
    }

    static std::string sendPOSTRequest(const std::string& url, const std::string& data, const std::vector<std::string> headers = {"Content-Type: application/json"}) {
        return sendRequest(url, headers, data);
    }

    static std::vector<std::string> sendParallelGETRequests(const std::vector<std::string>& urls, const std::vector<std::string>& headers = {}) {
        return sendParallelRequests(urls, headers, std::nullopt);
    }

    static std::vector<std::string> sendParallelPOSTRequests(const std::vector<std::string>& urls, const std::string& data, const std::vector<std::string>& headers = {}) {
        return sendParallelRequests(urls, headers, data);
    }

private:
    struct CurlDeleter {
        void operator()(CURL* ptr) const { if (ptr) curl_easy_cleanup(ptr); }
    };

    struct CurlSlistDeleter {
        void operator()(curl_slist* ptr) const { if (ptr) curl_slist_free_all(ptr); }
    };

    static size_t writeCallback(char* ptr, size_t size, size_t nmemb, std::string* data) {
        data->append(ptr, size * nmemb);
        return size * nmemb;
    }

    static std::string sendRequest(const std::string& url, const std::vector<std::string>& headers, std::optional<std::string> postData) {
        std::unique_ptr<CURL, CurlDeleter> curl(curl_easy_init());
        if (!curl) return "Error: Failed to initialize CURL.";

        std::string response;
        curl_slist* temp_list = nullptr;
        for (const auto& header : headers) {
            temp_list = curl_slist_append(temp_list, header.c_str());
        }
        std::unique_ptr<curl_slist, CurlSlistDeleter> header_list(temp_list);

        curl_easy_setopt(curl.get(), CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl.get(), CURLOPT_WRITEFUNCTION, writeCallback);
        curl_easy_setopt(curl.get(), CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl.get(), CURLOPT_TIMEOUT, 10L);  // Prevents hanging requests

        if (header_list) curl_easy_setopt(curl.get(), CURLOPT_HTTPHEADER, header_list.get());

        if (postData.has_value()) {
            curl_easy_setopt(curl.get(), CURLOPT_POST, 1L);
            curl_easy_setopt(curl.get(), CURLOPT_POSTFIELDS, postData->c_str());
        }

        CURLcode res = curl_easy_perform(curl.get());
        if (res != CURLE_OK) {
            return "Error: " + std::string(curl_easy_strerror(res));
        }

        return response;
    }

    static std::vector<std::string> sendParallelRequests(const std::vector<std::string>& urls, const std::vector<std::string>& headers, std::optional<std::string> postData) {
        std::vector<std::future<std::string>> futures;
        for (const auto& url : urls) {
            futures.emplace_back(std::async(std::launch::async, sendRequest, url, headers, postData));
        }

        std::vector<std::string> responses;
        for (auto& future : futures) {
            try {
                responses.push_back(future.get());
            } catch (const std::exception& e) {
                responses.push_back("Error: Exception in async request: " + std::string(e.what()));
            }
        }

        return responses;
    }
};

#endif // HTTP_CLIENT_H
