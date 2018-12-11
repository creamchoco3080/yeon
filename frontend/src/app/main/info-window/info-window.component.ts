import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { map, pluck } from 'rxjs/operators';

import { GraphService } from '../graph';
import { AuthService  } from '../../auth';
import { UserNode } from 'src/models';
import { ProfileComponent } from '../profile/profile.component';

@Component({
  selector: 'app-info-window',
  templateUrl: './info-window.component.html',
  styleUrls: ['./info-window.component.css']
})
export class InfoWindowComponent implements OnInit {

  @Input() profiles: any[];
  @Output() cancelSelected: EventEmitter<void> = new EventEmitter();

  friends: number[];
  pending: number[];

  confirmed: boolean = false;

  constructor(
    private graph: GraphService, 
    private auth: AuthService,
    private modal: NgbModal
    ) { }

  ngOnInit() {
    this.graph.getLevel(1).pipe(
      pluck('users'),
      map((users: UserNode[]) => users.map(user => user.id))
    ).subscribe((friends)=>{
      this.friends = friends;
    });
    this.updatePending();
  }

  updatePending() {
    this.graph.getNotifications().pipe(
      map((notifications: any[])=>{
        let receiver = notifications.map((noti)=>noti.receiver);
        let sender = notifications.map((noti)=>noti.sender);
        return receiver.concat(sender);
      }),
    ).subscribe((pending: any[])=>{
      this.pending = pending.filter(id => id !== parseInt(this.auth.userId));
    });
  }

  isPending(id) {
    return this.pending.includes(id);
  }

  isFriend(id) {
    return this.friends.includes(id);
  }

  confirmProfiles() {
    this.confirmed = true;
  }

  cancelProfiles() {
    this.cancelSelected.emit();
  }

  showProfile() {
    const modalConfig: any = {
      size: 'lg',
      backdrop: "static"
    };
    const signUpModal = this.modal.open(ProfileComponent, modalConfig);
    signUpModal.componentInstance.selectedNodes = this.profiles;
  }

  sendFriendRequest(id: string) {
    this.graph.sendFriendRequest(id).subscribe((res: any)=>{
      console.log('Friend request sent: ', res.createdTime);
      this.updatePending();
    });
  }

}
