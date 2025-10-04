import dotenv from "dotenv";

dotenv.config();

import minio from "minio";

class Client {
    constructor() {
        this.bucket = process.env.MINIO_BUCKET;
        this.client = new minio.Client({
            endPoint: process.env.MINIO_HOST,
            port: process.env.MINIO_PORT,
            useSSL: false,
            accessKey: process.env.MINIO_USER,
            secretKey: process.env.MINIO_PASSWORD
        });
        this.init().then(r => null);
    }

    async init() {
        try {
            const exists = await this.client.bucketExists(this.bucket);
            if (!exists) {
                await this.client.makeBucket(this.bucket, 'us-east-1');
                console.log(`Bucket created: ${this.bucket}`);
            } else {
                console.log(`Bucket exists: ${this.bucket}`);
            }
        } catch (err) {
            console.error('MinIO init error:', err);
        }
    }

    async upload(localPath, remoteName) {
        return new Promise((resolve, reject) => {
            this.client.fPutObject(this.bucket, remoteName, localPath, (err, etag) => {
                if (err) return reject(err);
                resolve(etag);
            });
        });
    }

    async download(remoteName, localPath) {
        return new Promise((resolve, reject) => {
            this.client.fGetObject(this.bucket, remoteName, localPath, (err) => {
                if (err) return reject(err);
                resolve();
            });
        });
    }

    async list() {
        return new Promise((resolve, reject) => {
            const objects = [];
            const stream = this.client.listObjectsV2(this.bucket, '', true);
            stream.on('data', obj => objects.push(obj));
            stream.on('end', () => resolve(objects));
            stream.on('error', err => reject(err));
        });
    }
}

export const storageClient = new Client();