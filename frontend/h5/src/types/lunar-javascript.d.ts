declare module 'lunar-javascript' {
  export class Solar {
    static fromYmd(year: number, month: number, day: number): Solar;
    static fromYmdHms(year: number, month: number, day: number, hour: number, minute: number, second: number): Solar;
    getLunar(): Lunar;
    getYear(): number;
    getMonth(): number;
    getDay(): number;
    getXingZuo(): string;
  }

  export class Lunar {
    static fromYmd(year: number, month: number, day: number): Lunar;
    static fromYmdHms(year: number, month: number, day: number, hour: number, minute: number, second: number): Lunar;
    getSolar(): Solar;
    getYear(): number;
    getMonth(): number;
    getDay(): number;
    getEightChar(): EightChar;
  }

  export class EightChar {
    getYear(): string;
    getMonth(): string;
    getDay(): string;
    getTime(): string;
    getYearWuXing(): string;
    getMonthWuXing(): string;
    getDayWuXing(): string;
    getTimeWuXing(): string;
  }
}
