/**
 * File System Helper - JSON data management
 */
import fs from 'fs/promises';
import { existsSync } from 'fs';

export class FileSystem {
    /**
     * Load JSON data from file
     * @param {string} filepath - Path to JSON file
     * @param {*} defaultValue - Default value if file doesn't exist
     * @returns {Promise<*>} Parsed JSON data
     */
    static async loadJSON(filepath, defaultValue = {}) {
        try {
            if (existsSync(filepath)) {
                const data = await fs.readFile(filepath, 'utf-8');
                return JSON.parse(data);
            }
        } catch (error) {
            console.error(`Error loading ${filepath}:`, error);
        }
        return defaultValue;
    }

    /**
     * Save JSON data to file
     * @param {string} filepath - Path to JSON file
     * @param {*} data - Data to save
     * @returns {Promise<boolean>} Success status
     */
    static async saveJSON(filepath, data) {
        try {
            await fs.writeFile(filepath, JSON.stringify(data, null, 2), 'utf-8');
            return true;
        } catch (error) {
            console.error(`Error saving ${filepath}:`, error);
            return false;
        }
    }
}
