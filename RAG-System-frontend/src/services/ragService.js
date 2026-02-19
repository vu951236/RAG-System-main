import axiosClient from "../api/axiosClient";

const ragService = {

    uploadFile: async (file) => {
        const formData = new FormData();
        formData.append("file", file);

        return axiosClient.post("/rag/upload", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
    },

    askQuestion: async (question) => {
        return axiosClient.post(
            "/rag/ask",
            { question },
            { responseType: "blob" }
        );
    },

};

export default ragService;
