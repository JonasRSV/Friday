
export class Command {
  constructor(keyword, scripts) {
    // keyword is a unique identifier of this command
    this.keyword = keyword;

    this.scripts = scripts;
  }
}